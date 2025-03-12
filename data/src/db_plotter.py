import geopandas as gpd
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import psycopg2
from matplotlib.colors import ListedColormap, Normalize
from matplotlib.patches import Patch
from matplotlib.ticker import ScalarFormatter
from shapely import wkb
from shapely.geometry import LineString
from shapely.ops import unary_union


class DBPlotter:
    """
    Class to plot data from the database.
    """

    def __init__(self, config):
        self.conf = config
        self.conn = None
        self.cur = None
        self.clean_boundary_names = None

        self.set_clean_boundary_names()

    def set_clean_boundary_names(self):
        """
        Set clean boundary names.
        """

        self.clean_boundary_names = {
            "uk_counties": "UK Counties and Unitary Authorities",
            "la_districts": "LA Districts",
            "lsoa": "LSOAs",
            "msoa": "MSOAs",
            "parishes": "Parishes",
            "sc_dz": "Scotland Data Zones",
            "ni_dz": "Northern Ireland Data Zones",
            "iom": "Isle of Man",
        }

    def connect_to_db(self, host=None, dbname=None, user=None, password=None):
        """
        Connect to database with provided credentials, or those in config file.
        """

        if not host or not dbname or not user or not password:
            host = self.conf["host"]
            dbname = self.conf["dbname"]
            user = self.conf["user"]
            password = self.conf["user_pass"]

            print("Connecting using db config from config file...")

        self.conn = psycopg2.connect(host=host, dbname=dbname, user=user, password=password)
        self.cur = self.conn.cursor()

        print("Connection successful.")

    #########################################################################
    ### Boundaries
    #########################################################################

    def get_boundary_geometry(self, boundary_identifier):
        """
        Given a boundary identifier, get the boundary data loaded from shapefile.
        """

        table_name = f"boundary_{boundary_identifier}"

        boundary_query = f"""
        SELECT gid, geom FROM "{table_name}"
        """

        self.cur.execute(boundary_query)
        boundary_geometry = self.cur.fetchall()

        return boundary_geometry

    def plot_boundary(self, boundary_identifier):
        """
        Get boundary geometry from database, create GeoDataFrame for fast plotting, and create plot.
        """

        boundary_geometry = self.get_boundary_geometry(boundary_identifier)

        data = []
        for row in boundary_geometry:
            geom = wkb.loads(row[1], hex=True)
            data.append({"id": row[0], "geometry": geom})

        gdf = gpd.GeoDataFrame(data, geometry="geometry")

        # Create plot
        fig, ax = plt.subplots(figsize=(10, 10))
        gdf.plot(ax=ax, color="white", edgecolor="black", linewidth=0.5)

        ax.set_title(f"{self.clean_boundary_names[boundary_identifier]}", fontsize=14)
        ax.set_xlabel("Eastings", fontsize=14)
        ax.set_ylabel("Northings", fontsize=14)
        ax.set_facecolor("lightgrey")
        ax.xaxis.set_major_formatter(ScalarFormatter(useMathText=True))
        ax.yaxis.set_major_formatter(ScalarFormatter(useMathText=True))
        ax.ticklabel_format(style="sci", axis="both", scilimits=(0, 0))

        plt.show()

    def plot_boundary_coloured_by_coastal(self, boundary_identifier, lines=None):
        """
        Get boundary geometry from the database, create a GeoDataFrame for fast plotting, and create a plot.
        Regions are colored based on the 'is_coastal' column (True/False).
        """

        # Get boundary geometry
        boundary_geometry = self.get_boundary_geometry(boundary_identifier)

        # Query to get 'is_coastal' data for each region
        query = f"""
            SELECT gid, is_coastal FROM boundary_{boundary_identifier};
        """

        self.cur.execute(query)
        coastal_data = self.cur.fetchall()

        # Convert coastal_data into a dictionary for easy lookup
        coastal_dict = {row[0]: row[1] for row in coastal_data}

        # Prepare GeoDataFrame
        data = []
        for row in boundary_geometry:
            row_gid = row[0]
            geom = wkb.loads(row[1], hex=True)
            is_coastal = coastal_dict.get(row_gid)  # Get coastal status

            data.append({"id": row_gid, "geometry": geom, "is_coastal": is_coastal})

        gdf = gpd.GeoDataFrame(data, geometry="geometry")

        # Define cmap: Coastal = Blue, Non-coastal = Gray, Unknown = White
        cmap = ListedColormap(["gray", "blue", "white"])
        colors = gdf["is_coastal"].map({False: 0, True: 1, None: 2})

        # Create plot
        fig, ax = plt.subplots(figsize=(10, 10))

        # Plot regions colored by is_coastal
        gdf.plot(
            ax=ax,
            color=[cmap(c) for c in colors],
            edgecolor="black",
            linewidth=0.5 if lines else 0,
        )

        # Create legend manually
        from matplotlib.patches import Patch

        legend_patches = [
            Patch(color="gray", label="Non-coastal"),
            Patch(color="blue", label="Coastal"),
            Patch(color="white", label="Unknown"),
        ]
        ax.legend(handles=legend_patches, title="Region Type")

        # Customize the plot
        ax.set_title(f"{self.clean_boundary_names[boundary_identifier]}: Coastal vs Non-Coastal", fontsize=12)
        ax.set_xlabel("Eastings", fontsize=14)
        ax.set_ylabel("Northings", fontsize=14)
        ax.set_facecolor("white")
        ax.xaxis.set_major_formatter(plt.ScalarFormatter(useMathText=True))
        ax.yaxis.set_major_formatter(plt.ScalarFormatter(useMathText=True))
        ax.ticklabel_format(style="sci", axis="both", scilimits=(0, 0))

        plt.show()

    #########################################################################
    ### CHESS-SCAPE grid cells
    #########################################################################

    def get_grid_geometry(self):
        """
        Get the CHESS-SCAPE grid cells stored in the database.
        """

        table_name = "chess_scape_grid"

        grid_cell_query = f"""
        SELECT grid_cell_id, geometry, bias_corrected, coastal_info FROM "{table_name}"
        """

        self.cur.execute(grid_cell_query)
        grid_geometry = self.cur.fetchall()

        return grid_geometry

    def plot_chess_grid_cells(self, merged=True, viewbox=None):
        """
        Merge and then plot the CHESS-SCAPE grid, identifying bias and non-bias corrected data.
        """

        grid_geometry = self.get_grid_geometry()

        data = []
        for row in grid_geometry:
            geom = wkb.loads(row[1], hex=True)
            data.append({"id": row[0], "geometry": geom, "bias_corrected": row[2]})

        gdf = gpd.GeoDataFrame(data, geometry="geometry")

        if merged:
            grouped = gdf.groupby("bias_corrected")["geometry"].apply(lambda x: unary_union(x))
            gdf = gpd.GeoDataFrame(grouped, geometry="geometry").reset_index()

        gdf.sort_values(by=["bias_corrected"], inplace=True)
        cmap = ListedColormap(["#F7D9C4", "#DBCDF0"])

        # Create plot
        fig, ax = plt.subplots(figsize=(10, 10))
        gdf.plot(
            ax=ax,
            column="bias_corrected",
            cmap=cmap,
            legend=True,
            edgecolor="black",
            linewidth=0.5,
        )

        # Change viewbox if supplied
        if viewbox:
            x_min, x_max, y_min, y_max = viewbox
            ax.set_xlim([x_min, x_max])
            ax.set_ylim([y_min, y_max])

        ax.set_title("CHESS-SCAPE Grid Cells", fontsize=14)
        ax.set_xlabel("Eastings", fontsize=14)
        ax.set_ylabel("Northings", fontsize=14)
        ax.xaxis.set_major_formatter(ScalarFormatter(useMathText=True))
        ax.yaxis.set_major_formatter(ScalarFormatter(useMathText=True))
        ax.ticklabel_format(style="sci", axis="both", scilimits=(0, 0))

        legend_labels = {"False": "Non bias corrected", "True": "Bias corrected"}
        handles = [
            Patch(color="#F7D9C4", label=legend_labels["False"]),
            Patch(color="#DBCDF0", label=legend_labels["True"]),
        ]

        ax.legend(handles=handles, title="Available Data", loc="upper right")

        plt.show()

    #########################################################################
    ### CHESS-SCAPE grid cells coloured by variable/data
    #########################################################################

    def get_chess_data(self, rcp, season, variable, decade):
        """
        Get the cached CHESS-SCAPE variable data required, indexed by gid.
        """

        table_name = f"chess_scape_rcp{rcp}_{season}"
        col_name = f"{variable}_{decade}"

        chess_query = f"""
        SELECT grid_cell_id, "{col_name}" FROM "{table_name}"
        """

        self.cur.execute(chess_query)
        chess_data = self.cur.fetchall()

        return chess_data

    def plot_chess_grid_and_data(self, rcp, season, variable, decade, viewbox=None):
        """
        Plot the CHESS-SCAPE grid cells colored by the data values from the specified
        variable, season, and decade.
        """

        # Get grid geometry and chess data
        grid_geometry = self.get_grid_geometry()
        chess_data = self.get_chess_data(rcp, season, variable, decade)

        # Convert chess_data into a dictionary for easy lookup
        chess_data_dict = {row[0]: row[1] for row in chess_data}

        # Create the GeoDataFrame
        data = []
        for row in grid_geometry:
            grid_cell_id = row[0]
            geom = wkb.loads(row[1], hex=True)
            data_value = chess_data_dict.get(grid_cell_id, np.nan)  # Get the data value, default to NaN if not present
            data.append({"id": grid_cell_id, "geometry": geom, "data_value": data_value})

        gdf = gpd.GeoDataFrame(data, geometry="geometry")

        # Sort GeoDataFrame by data_value
        gdf.sort_values(by="data_value", inplace=True)

        # Normalize the data for the color map
        norm = Normalize(vmin=gdf["data_value"].min(), vmax=gdf["data_value"].max())

        # Choose cmap
        cmap = plt.cm.viridis

        # Create plot
        fig, ax = plt.subplots(figsize=(10, 10))
        gdf.plot(
            ax=ax,
            column="data_value",
            cmap=cmap,
            legend=False,
            edgecolor="black",
            linewidth=0,
            norm=norm,
        )

        # Add color bar

        variable_units = {
            "pr": "mm/day",
            "sfcWind": "m/s",
            "rsds": "W/m^2",
            "tas": "degrees Celsius",
            "tasmin": "degrees Celsius",
            "tasmax": "degrees Celsius",
        }

        sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
        sm.set_array(gdf["data_value"])
        cbar = fig.colorbar(sm, ax=ax)
        cbar.set_label(f"{variable_units[variable]}")

        # Change viewbox if supplied
        if viewbox:
            x_min, x_max, y_min, y_max = viewbox
            ax.set_xlim([x_min, x_max])
            ax.set_ylim([y_min, y_max])

        ax.set_title(f"CHESS-SCAPE data: {variable} ({decade}) at RCP{rcp/10}", fontsize=14)
        ax.set_xlabel("Eastings", fontsize=14)
        ax.set_ylabel("Northings", fontsize=14)
        ax.xaxis.set_major_formatter(mpl.ticker.ScalarFormatter(useMathText=True))
        ax.yaxis.set_major_formatter(mpl.ticker.ScalarFormatter(useMathText=True))
        ax.ticklabel_format(style="sci", axis="both", scilimits=(0, 0))

        plt.show()

    def plot_chess_grid_cells_coloured_by_coastal(self, merged=True, viewbox=None):
        """
        Merge and then plot the CHESS-SCAPE grid, coloured by coastal proximity.
        """

        grid_geometry = self.get_grid_geometry()

        data = []
        for row in grid_geometry:
            geom = wkb.loads(row[1], hex=True)
            data.append(
                {
                    "id": row[0],
                    "geometry": geom,
                    "bias_corrected": row[2],
                    "coastal_info": row[3],
                }
            )

        gdf = gpd.GeoDataFrame(data, geometry="geometry")

        if merged:
            grouped = gdf.groupby("coastal_info")["geometry"].apply(lambda x: unary_union(x))
            gdf = gpd.GeoDataFrame(grouped, geometry="geometry").reset_index()

        gdf.sort_values(by=["coastal_info"], inplace=True)

        # Create plot
        fig, ax = plt.subplots(figsize=(40, 30))
        gdf.plot(
            ax=ax,
            column="coastal_info",
            cmap="viridis",
            legend=True,
        )

        # Change viewbox if supplied
        if viewbox:
            x_min, x_max, y_min, y_max = viewbox
            ax.set_xlim([x_min, x_max])
            ax.set_ylim([y_min, y_max])

        ax.set_title("CHESS-SCAPE Grid Cells (coloured by coastal proximity)", fontsize=14)
        ax.set_xlabel("Eastings", fontsize=14)
        ax.set_ylabel("Northings", fontsize=14)
        ax.xaxis.set_major_formatter(ScalarFormatter(useMathText=True))
        ax.yaxis.set_major_formatter(ScalarFormatter(useMathText=True))
        ax.ticklabel_format(style="sci", axis="both", scilimits=(0, 0))

        plt.show()

    #########################################################################
    ### Region geometry and overlapping grid cells
    #########################################################################

    def get_geometry_by_gid(self, boundary_identifier, region_gid):
        """
        Given a boundary identifier and a region gid, return the geometry.
        """

        table_name = f"boundary_{boundary_identifier}"

        gid_query = f"""
        SELECT s.gid, s.geom
        FROM {table_name} s
        WHERE s.gid = %s;
        """

        self.cur.execute(gid_query, (region_gid,))
        region_geometry = self.cur.fetchall()

        return region_geometry

    def get_region_name_by_gid(self, boundary_identifier, region_gid):
        """
        Given a boundary identifier and region gid, get the region name.
        """

        name_cols = {
            "uk_counties": "CTYUA23NM",
            "la_districts": "LAD23NM",
            "lsoa": "LSOA21NM",
            "msoa": "MSOA21NM",
            "parishes": "PAR23NM",
            "sc_dz": "Name",
            "ni_dz": "DZ2021_nm",
            "iom": "NAME_ENGLI",
        }

        column_name = name_cols[boundary_identifier]
        table_name = f"boundary_{boundary_identifier}"

        get_region_name_query = f"""
        SELECT {column_name}
        FROM "{table_name}"
        WHERE gid = %s
        """

        self.cur.execute(get_region_name_query, (region_gid,))
        region_name = self.cur.fetchone()[0]

        return region_name

    def get_overlapping_cells(self, boundary_identifier, region_gid):
        """
        Using the boundary overlap table, get the overlapping grid cells with the geometry. Note that if
        no overlaps were found previously, the closest grid cell was stored.
        """

        overlap_table_name = f"grid_overlaps_{boundary_identifier}"
        chess_grid_table_name = "chess_scape_grid"

        get_overlap_query = f"""
        SELECT o.grid_cell_id, g.geometry, g.bias_corrected, o.is_overlap, g.coastal_info
        FROM "{overlap_table_name}" AS o
        JOIN "{chess_grid_table_name}" AS g
        ON o.grid_cell_id = g.grid_cell_id
        WHERE o.gid = %s;
        """

        self.cur.execute(get_overlap_query, (region_gid,))
        results = self.cur.fetchall()

        print(f"Cells found: {len(results)}")

        return results

    def plot_region_and_overlapping_cells(self, boundary_identifier, region_gid):
        """
        Plot a region from a boundary, and its overlapping grid cells.
        """

        # Get data to do with region
        region_geometry = self.get_geometry_by_gid(boundary_identifier, region_gid)
        region_name = self.get_region_name_by_gid(boundary_identifier, region_gid)

        data = []
        for row in region_geometry:
            geom = wkb.loads(row[1], hex=True)
            data.append({"id": row[0], "geometry": geom})

        gdf = gpd.GeoDataFrame(data, geometry="geometry")

        # Get overlapping cell data
        cell_geometry = self.get_overlapping_cells(boundary_identifier, region_gid)

        data = []
        for row in cell_geometry:
            geom = wkb.loads(row[1], hex=True)
            data.append(
                {
                    "id": row[0],
                    "geometry": geom,
                    "bias_corrected": row[2],
                    "is_overlap": row[3],
                }
            )

        cell_gdf = gpd.GeoDataFrame(data, geometry="geometry")

        # Get colour based on available data
        is_bias_corrected = str(cell_gdf["bias_corrected"].unique().tolist()[0])

        if is_bias_corrected == "False":
            color = "#F7D9C4"
        elif is_bias_corrected == "True":
            color = "#DBCDF0"
        else:
            color = "none"
            print("Unknown data type. Setting colour to 'none'.")

        legend_labels = {"False": "Non bias corrected", "True": "Bias corrected"}
        handles = [
            Patch(color=color, label=legend_labels[is_bias_corrected]),
        ]

        # Create plot
        fig, ax = plt.subplots(figsize=(10, 10))

        cell_gdf.plot(ax=ax, color=color, linewidth=0.5, edgecolor="black", alpha=0.5)
        gdf.plot(ax=ax, color="none", edgecolor="black")

        # If single cell, draw line between closest single cell and the centroid of the geometry

        if len(cell_gdf) == 1 and not cell_gdf["is_overlap"].iloc[0]:
            geom_centroid = gdf.union_all().centroid
            cell_centroid = cell_gdf.union_all().centroid
            line_geom = LineString([geom_centroid, cell_centroid])
            line_gdf = gpd.GeoDataFrame(geometry=[line_geom])
            grid_cell_id = cell_gdf["id"].iloc[0]

            line_gdf.plot(ax=ax, color="pink", linestyle="--")
            handles.append(Patch(color="pink", label=f"Closest cell: {grid_cell_id}"))

        # Other things
        ax.set_title(
            f"Overlapping grid cells: {self.clean_boundary_names[boundary_identifier]} - {region_gid}, {region_name}",
            fontsize=14,
        )
        ax.set_xlabel("Eastings", fontsize=14)
        ax.set_ylabel("Northings", fontsize=14)
        ax.xaxis.set_major_formatter(ScalarFormatter(useMathText=True))
        ax.yaxis.set_major_formatter(ScalarFormatter(useMathText=True))
        ax.ticklabel_format(style="sci", axis="both", scilimits=(0, 0))
        ax.legend(handles=handles, title="Available Data", loc="upper right")

        plt.show()

    def plot_region_and_overlapping_cells_coloured_by_coastal(self, boundary_identifier, region_gid):
        """
        Plot a region from a boundary, and its overlapping grid cells, coloured by the coastal_info column.
        """

        # Get data to do with region
        region_geometry = self.get_geometry_by_gid(boundary_identifier, region_gid)
        region_name = self.get_region_name_by_gid(boundary_identifier, region_gid)

        data = []
        for row in region_geometry:
            geom = wkb.loads(row[1], hex=True)
            data.append({"id": row[0], "geometry": geom})

        gdf = gpd.GeoDataFrame(data, geometry="geometry")

        # Get overlapping cell data
        cell_geometry = self.get_overlapping_cells(boundary_identifier, region_gid)

        data = []
        for row in cell_geometry:
            geom = wkb.loads(row[1], hex=True)
            data.append(
                {"id": row[0], "geometry": geom, "bias_corrected": row[2], "is_overlap": row[3], "coastal_info": row[4]}
            )

        cell_gdf = gpd.GeoDataFrame(data, geometry="geometry")

        # Create plot
        fig, ax = plt.subplots(figsize=(10, 10))

        # Plot GeoDataFrame with color based on 'coastal_info'
        cell_gdf.plot(
            ax=ax, column="coastal_info", cmap="viridis", legend=True, linewidth=0.5, edgecolor="black", alpha=0.5
        )
        gdf.plot(ax=ax, color="none", edgecolor="black")

        # Other things
        ax.set_title(
            f"Overlapping grid cells coloured by coastal proximity: {self.clean_boundary_names[boundary_identifier]} - {region_gid}, {region_name}",
            fontsize=14,
        )
        ax.set_xlabel("Eastings", fontsize=14)
        ax.set_ylabel("Northings", fontsize=14)
        ax.xaxis.set_major_formatter(ScalarFormatter(useMathText=True))
        ax.yaxis.set_major_formatter(ScalarFormatter(useMathText=True))
        ax.ticklabel_format(style="sci", axis="both", scilimits=(0, 0))

        plt.show()

    def plot_region_and_overlapping_cells_with_colour(
        self, boundary_identifier, region_gid, rcp, season, variable, decade
    ):
        """
        Plot a region from a boundary, and its overlapping grid cells, colored by the data values
        for a specified variable, season, and decade.
        """

        # Get data to do with region
        region_geometry = self.get_geometry_by_gid(boundary_identifier, region_gid)
        region_name = self.get_region_name_by_gid(boundary_identifier, region_gid)

        region_data = []
        for row in region_geometry:
            geom = wkb.loads(row[1], hex=True)
            region_data.append({"id": row[0], "geometry": geom})

        region_gdf = gpd.GeoDataFrame(region_data, geometry="geometry")

        # Get overlapping cell data
        cell_geometry = self.get_overlapping_cells(boundary_identifier, region_gid)
        chess_data = self.get_chess_data(rcp, season, variable, decade)

        # Convert chess_data into a dictionary for easy lookup
        chess_data_dict = {row[0]: row[1] for row in chess_data}

        cell_data = []
        for row in cell_geometry:
            grid_cell_id = row[0]
            geom = wkb.loads(row[1], hex=True)
            data_value = chess_data_dict.get(grid_cell_id, np.nan)  # Get the data value, default to NaN if not present
            cell_data.append(
                {
                    "id": grid_cell_id,
                    "geometry": geom,
                    "data_value": data_value,
                    "is_overlap": row[3],
                }
            )

        cell_gdf = gpd.GeoDataFrame(cell_data, geometry="geometry")

        # Sort GeoDataFrame by data_value
        cell_gdf.sort_values(by="data_value", inplace=True)

        # Normalize the data for the color map
        norm = Normalize(vmin=cell_gdf["data_value"].min(), vmax=cell_gdf["data_value"].max())

        # Choose cmap
        cmap = plt.cm.viridis

        # Create plot
        fig, ax = plt.subplots(figsize=(10, 10))

        # Plot the overlapping cells colored by data_value
        cell_gdf.plot(
            ax=ax,
            column="data_value",
            cmap=cmap,
            legend=False,
            edgecolor="black",
            linewidth=0,
            alpha=1,
            norm=norm,
        )

        # Add color bar

        variable_units = {
            "pr": "mm/day",
            "sfcWind": "m/s",
            "rsds": "W/m^2",
            "tas": "degrees Celsius",
            "tasmin": "degrees Celsius",
            "tasmax": "degrees Celsius",
        }

        sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
        sm.set_array(cell_gdf["data_value"])
        cbar = fig.colorbar(sm, ax=ax)
        cbar.set_label(f"{variable_units[variable]}")

        # Plot the region geometry
        region_gdf.plot(ax=ax, color="none", edgecolor="black", linewidth=2)

        # If there is a single cell, draw a line between the region and the grid cell
        if len(cell_gdf) == 1 and not cell_gdf["is_overlap"].iloc[0]:
            geom_centroid = region_gdf.unary_union.centroid
            cell_centroid = cell_gdf.unary_union.centroid
            line_geom = LineString([geom_centroid, cell_centroid])
            line_gdf = gpd.GeoDataFrame(geometry=[line_geom])
            grid_cell_id = cell_gdf["id"].iloc[0]

            line_gdf.plot(ax=ax, color="pink", linestyle="--")
            ax.legend(
                handles=[Patch(color="pink", label=f"Closest cell: {grid_cell_id}")],
                loc="upper right",
            )

        # Add title and labels
        ax.set_title(
            f"Overlapping grid cells: {self.clean_boundary_names[boundary_identifier]} - {region_gid}, {region_name}",
            fontsize=14,
        )
        ax.set_xlabel("Eastings", fontsize=14)
        ax.set_ylabel("Northings", fontsize=14)
        ax.xaxis.set_major_formatter(plt.ScalarFormatter(useMathText=True))
        ax.yaxis.set_major_formatter(plt.ScalarFormatter(useMathText=True))
        ax.ticklabel_format(style="sci", axis="both", scilimits=(0, 0))

        plt.show()

    def plot_region_and_overlapping_cells_with_coastal_colour(self, boundary_identifier, region_gid):
        """
        Plot a region from a boundary, and its overlapping grid cells, colored by the data values
        for a specified variable, season, and decade.
        """

        # Get data to do with region
        region_geometry = self.get_geometry_by_gid(boundary_identifier, region_gid)
        region_name = self.get_region_name_by_gid(boundary_identifier, region_gid)

        region_data = []
        for row in region_geometry:
            geom = wkb.loads(row[1], hex=True)
            region_data.append({"id": row[0], "geometry": geom})

        region_gdf = gpd.GeoDataFrame(region_data, geometry="geometry")

        # Get overlapping cell data
        cell_geometry = self.get_overlapping_cells(boundary_identifier, region_gid)
        chess_data = self.get_chess_data(rcp, season, variable, decade)

        # Convert chess_data into a dictionary for easy lookup
        chess_data_dict = {row[0]: row[1] for row in chess_data}

        cell_data = []
        for row in cell_geometry:
            grid_cell_id = row[0]
            geom = wkb.loads(row[1], hex=True)
            data_value = chess_data_dict.get(grid_cell_id, np.nan)  # Get the data value, default to NaN if not present
            cell_data.append(
                {
                    "id": grid_cell_id,
                    "geometry": geom,
                    "data_value": data_value,
                    "is_overlap": row[3],
                }
            )

        cell_gdf = gpd.GeoDataFrame(cell_data, geometry="geometry")

        # Sort GeoDataFrame by data_value
        cell_gdf.sort_values(by="data_value", inplace=True)

        # Normalize the data for the color map
        norm = Normalize(vmin=cell_gdf["data_value"].min(), vmax=cell_gdf["data_value"].max())

        # Choose cmap
        cmap = plt.cm.viridis

        # Create plot
        fig, ax = plt.subplots(figsize=(10, 10))

        # Plot the overlapping cells colored by data_value
        cell_gdf.plot(
            ax=ax,
            column="data_value",
            cmap=cmap,
            legend=False,
            edgecolor="black",
            linewidth=0,
            alpha=1,
            norm=norm,
        )

        # Add color bar

        variable_units = {
            "pr": "mm/day",
            "sfcWind": "m/s",
            "rsds": "W/m^2",
            "tas": "degrees Celsius",
            "tasmin": "degrees Celsius",
            "tasmax": "degrees Celsius",
        }

        sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
        sm.set_array(cell_gdf["data_value"])
        cbar = fig.colorbar(sm, ax=ax)
        cbar.set_label(f"{variable_units[variable]}")

        # Plot the region geometry
        region_gdf.plot(ax=ax, color="none", edgecolor="black", linewidth=2)

        # If there is a single cell, draw a line between the region and the grid cell
        if len(cell_gdf) == 1 and not cell_gdf["is_overlap"].iloc[0]:
            geom_centroid = region_gdf.unary_union.centroid
            cell_centroid = cell_gdf.unary_union.centroid
            line_geom = LineString([geom_centroid, cell_centroid])
            line_gdf = gpd.GeoDataFrame(geometry=[line_geom])
            grid_cell_id = cell_gdf["id"].iloc[0]

            line_gdf.plot(ax=ax, color="pink", linestyle="--")
            ax.legend(
                handles=[Patch(color="pink", label=f"Closest cell: {grid_cell_id}")],
                loc="upper right",
            )

        # Add title and labels
        ax.set_title(
            f"Overlapping grid cells: {self.clean_boundary_names[boundary_identifier]} - {region_gid}, {region_name}",
            fontsize=14,
        )
        ax.set_xlabel("Eastings", fontsize=14)
        ax.set_ylabel("Northings", fontsize=14)
        ax.xaxis.set_major_formatter(plt.ScalarFormatter(useMathText=True))
        ax.yaxis.set_major_formatter(plt.ScalarFormatter(useMathText=True))
        ax.ticklabel_format(style="sci", axis="both", scilimits=(0, 0))

        plt.show()

    def get_no_overlap_geometry(self, boundary_identifier):
        """
        Get the grid cells stored in the overlap table that are not overlapping with gids(i.e.
        is_overlap column is False).
        """

        boundary_table = f"boundary_{boundary_identifier}"
        overlap_table = f"grid_overlaps_{boundary_identifier}"

        no_overlap_query = f"""
            SELECT bt.gid, bt.geom
            FROM "{boundary_table}" bt
            WHERE bt.gid IN (
                SELECT ot.gid
                FROM "{overlap_table}" ot
                WHERE ot.is_overlap = FALSE
            )
        """

        self.cur.execute(no_overlap_query)
        no_overlap_geometry = self.cur.fetchall()

        return no_overlap_geometry

    def plot_no_overlap_locations(self, boundary_identifier, viewbox=None, show_labels=True):
        """
        Plot the location of the regions with no overlaps on the grid cell plot.
        """

        grid_geometry = self.get_grid_geometry()
        no_overlap_geometry = self.get_no_overlap_geometry(boundary_identifier)

        if len(no_overlap_geometry) == 0:
            print(f"No overlaps found for: {boundary_identifier}")
            return

        data = []
        for row in grid_geometry:
            geom = wkb.loads(row[1], hex=True)
            data.append({"id": row[0], "geometry": geom, "bias_corrected": row[2]})

        gdf = gpd.GeoDataFrame(data, geometry="geometry")

        grouped = gdf.groupby("bias_corrected")["geometry"].apply(lambda x: unary_union(x))
        gdf = gpd.GeoDataFrame(grouped, geometry="geometry").reset_index()

        gdf.sort_values(by=["bias_corrected"], inplace=True)
        cmap = ListedColormap(["#F7D9C4", "#DBCDF0"])

        # Create plot
        fig, ax = plt.subplots(figsize=(10, 10))
        gdf.plot(
            ax=ax,
            column="bias_corrected",
            cmap=cmap,
            legend=True,
            edgecolor="black",
            linewidth=0.5,
        )

        # Create gdf for no overlap geometry
        if len(no_overlap_geometry) > 0:
            print(f"{len(no_overlap_geometry)} no overlap regions found.")
            data = []
            for row in no_overlap_geometry:
                geom = wkb.loads(row[1], hex=True)
                data.append({"gid": row[0], "geometry": geom})

            no_overlap_gdf = gpd.GeoDataFrame(data, geometry="geometry")
            centroids = no_overlap_gdf.geometry.centroid

            no_overlap_gdf.plot(
                ax=ax,
                color="red",
                edgecolor="red",
                linewidth=0.5,
            )
            ax.scatter(centroids.x, centroids.y, color="black", marker="x", s=100)

        # Annotate each centroid with its corresponding gid
        if show_labels:
            for idx, row in no_overlap_gdf.iterrows():
                ax.text(
                    row.geometry.centroid.x,
                    row.geometry.centroid.y,
                    str(row.gid),
                    fontsize=9,
                    ha="left",
                    color="black",
                    clip_on=True,
                )

        # Change viewbox if supplied
        if viewbox:
            x_min, x_max, y_min, y_max = viewbox
            ax.set_xlim([x_min, x_max])
            ax.set_ylim([y_min, y_max])

        ax.set_title(
            f"{self.clean_boundary_names[boundary_identifier]}: no overlapping grid cell regions",
            fontsize=14,
        )
        ax.set_xlabel("Eastings", fontsize=14)
        ax.set_ylabel("Northings", fontsize=14)
        ax.xaxis.set_major_formatter(ScalarFormatter(useMathText=True))
        ax.yaxis.set_major_formatter(ScalarFormatter(useMathText=True))
        ax.ticklabel_format(style="sci", axis="both", scilimits=(0, 0))

        legend_labels = {"False": "Non bias corrected", "True": "Bias corrected"}
        handles = [
            Patch(color="#F7D9C4", label=legend_labels["False"]),
            Patch(color="#DBCDF0", label=legend_labels["True"]),
        ]

        ax.legend(handles=handles, title="Available Data", loc="upper left")

        plt.show()

    #########################################################################
    ### Boundary coloured by cached CHESS-SCAPE data
    #########################################################################

    def get_cached_chess_data(self, boundary_identifier, variable, decade, rcp, season):
        """
        Get the cached CHESS-SCAPE variable data required, indexed by gid.
        """

        table_name = f"cache_{boundary_identifier}_to_rcp{rcp}_{season}"
        col_name = f"{variable}_{decade}"

        chess_query = f"""
        SELECT gid, "{col_name}" FROM "{table_name}"
        """

        self.cur.execute(chess_query)
        chess_data = self.cur.fetchall()

        return chess_data

    def plot_boundary_coloured_by_cache(self, boundary_identifier, variable, decade, rcp, season, lines=None):
        """
        Get boundary geometry from database, create GeoDataFrame for fast plotting, and create plot.
        Regions are colored by the data returned from the cached CHESS-SCAPE data.
        """

        # Get boundary geometry
        boundary_geometry = self.get_boundary_geometry(boundary_identifier)

        # Get cached data for the boundary
        chess_data = self.get_cached_chess_data(boundary_identifier, variable, decade, rcp, season)

        # Convert chess_data into a dictionary for easy lookup
        chess_data_dict = {row[0]: row[1] for row in chess_data}

        # Prepare GeoDataFrame
        data = []
        for row in boundary_geometry:
            row_gid = row[0]
            geom = wkb.loads(row[1], hex=True)
            data_value = chess_data_dict.get(row_gid, np.nan)
            data.append({"id": row_gid, "geometry": geom, "data_value": data_value})

        gdf = gpd.GeoDataFrame(data, geometry="geometry")

        # Sort GeoDataFrame by data_value
        gdf.sort_values(by="data_value", inplace=True)

        # Normalize the data for the color map
        norm = Normalize(vmin=gdf["data_value"].min(), vmax=gdf["data_value"].max())

        # Choose cmap
        cmap = plt.cm.viridis

        # Create plot
        fig, ax = plt.subplots(figsize=(10, 10))

        # Plot regions colored by data_value
        gdf.plot(
            ax=ax,
            column="data_value",
            cmap=cmap,
            legend=False,
            edgecolor="black",
            linewidth=0.5 if lines else 0,
            norm=norm,
        )

        # Add color bar

        variable_units = {
            "pr": "mm/day",
            "sfcWind": "m/s",
            "rsds": "W/m^2",
            "tas": "degrees Celsius",
            "tasmin": "degrees Celsius",
            "tasmax": "degrees Celsius",
        }

        sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
        sm.set_array(gdf["data_value"])
        cbar = fig.colorbar(sm, ax=ax)
        cbar.set_label(f"{variable_units[variable]}")

        # Customize the plot

        ax.set_title(
            f"{self.clean_boundary_names[boundary_identifier]}: coloured by {season} {variable} ({decade}) at RCP{rcp/10}",
            fontsize=12,
        )

        ax.set_xlabel("Eastings", fontsize=14)
        ax.set_ylabel("Northings", fontsize=14)
        # ax.set_facecolor("lightgrey")
        ax.set_facecolor("white")
        ax.xaxis.set_major_formatter(plt.ScalarFormatter(useMathText=True))
        ax.yaxis.set_major_formatter(plt.ScalarFormatter(useMathText=True))
        ax.ticklabel_format(style="sci", axis="both", scilimits=(0, 0))

        plt.show()

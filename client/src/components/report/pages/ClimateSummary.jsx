import { Image, Link, Text, View } from '@react-pdf/renderer';

import DecreaseArrow from '../../../images/buttons/decrease.png';
import IncreaseArrow from '../../../images/buttons/increase.png';
import CloudIcon from '../../../images/climate/Cloud Cover.png';
import RainIcon from '../../../images/climate/Rain.png';
import TemperatureIcon from '../../../images/climate/Temperature.png';
import WindIcon from '../../../images/climate/Wind Speed.png';
import { climateVariables, formatClimateData } from '../../../utils/climateUtils';
import { andify } from "../../../utils/utils";
import { reportStyles as styles } from '../reportStyles';
import { formatLineBreaks } from '../textFormattingUtils';

const getClimateIcon = (variable) => {
    const iconMap = {
        'tas': TemperatureIcon,
        'pr': RainIcon,
        'rsds': CloudIcon,
        'sfcWind': WindIcon,
    };
    return iconMap[variable] || TemperatureIcon;
};

const getArrowIcon = (arrow) => {
    switch (arrow) {
        case 'up': return IncreaseArrow;
        case 'down': return DecreaseArrow;
        case 'none': return null;
        default: return null;
    }
};

const ClimateSummaryPDF = ({ climatePrediction, regions, rcp, season }) => {
    if (!climatePrediction || climatePrediction.length === 0) {
        return (
            <View style={styles.section}>
                <Text style={styles.subtitle}>Climate Summary</Text>
                <Text style={styles.bodyText}>No climate data available for this region.</Text>
            </View>
        );
    }

    return (
        <View style={styles.section}>
            <Text style={styles.subtitle}>EXPLORE YOUR LOCAL CLIMATE</Text>
            {regions && regions.length > 0 && rcp && season && (
                <>
                    <Text style={styles.bodyText}>
                        For <Text style={[styles.bodyText, { fontWeight: 'bold' }]}>{andify(regions.map(region => region.name))}</Text>
                        {' '}under the
                        <Text style={[styles.bodyText, { fontWeight: 'bold' }]}>
                            {rcp === 'rcp60' ? ' existing global policies ' : ' worst case scenario '}
                        </Text>
                        (equivalent to global warming level of {rcp === 'rcp60' ? '2.0-3.7C which is RCP 6.0' : '3.2-5.4C which is RCP 8.5'})
                        {' '}the <Text style={[styles.bodyText, { fontWeight: 'bold' }]}>{season}</Text>
                        {' '}average climate change for 2070 compared with local records for the 1980s is expected to be:
                    </Text>
                </>
            )}

            <View style={styles.climateContainer}>
                {climateVariables.map((item, index) => {
                    const climateData = formatClimateData(climatePrediction, item.variable, item.name, item.units, 2070);
                    const iconSrc = getClimateIcon(item.variable);
                    const arrowSrc = getArrowIcon(climateData.arrow);

                    return (
                        <View key={index} style={[styles.climateItem, { width: '24%' }]}>
                            <View style={styles.iconContainer}>
                                {arrowSrc && (
                                    <Image src={arrowSrc} style={styles.arrow} />
                                )}
                                <Image src={iconSrc} style={styles.icon} />
                            </View>
                            <Text style={styles.climateVariable}>{item.name}</Text>
                            <Text style={styles.climateValue}>{formatLineBreaks(climateData.change)}</Text>
                        </View>
                    );
                })}
            </View>

            <Text style={styles.bodyText}>
                Note: Yearly average climate change does not always reflect the extremes of summer and winter.
                {'\n\n'}
                Data source: The current iteration of the tool uses climate data from the{" "}
                <Link src="https://catalogue.ceda.ac.uk/uuid/8194b416cbee482b89e0dfbe17c5786c">CHESS-SCAPE</Link>{" "}
                dataset. CHESS-SCAPE provides bias-corrected data for England, Scotland, Wales, and the Isle of Man.
                CHESS-SCAPE provides non bias-corrected data for Northern Ireland and the Isles of Scilly. The tool
                displays RCP 6.0 and RCP 8.5. For more information, please see the{" "}
                <Link src="https://www.ecehh.org/wp/wp-content/uploads/2021/09/LCAT-USER-GUIDE-June-2025-update.pdf">
                    LCAT Handbook
                </Link>
                .
            </Text>
        </View>
    );
};

export default ClimateSummaryPDF;
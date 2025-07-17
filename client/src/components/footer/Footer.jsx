/* Development before 2024 Copyright (C) Then Try This and University of Exeter
Development from 2024 Copyright (C) University of Exeter

This program is free software: you can redistribute it and/or modify
it under the terms of the Common Good Public License Beta 1.0 as
published at http://www.cgpl.org

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
Common Good Public License Beta 1.0 for more details. */

/* global gtag */

import "./Footer.css";

import { PDFDownloadLink } from '@react-pdf/renderer';
import React from "react";

import ClimateReport from "../report/report";
import AdaptationGuide from "./AdaptationGuide";
import ContactUs from "./ContactUs";
import FooterLogos from "./FooterLogos";
import FooterText from "./FooterText";
import Handbook from "./Handbook";

const Footer = ({ regions, climatePrediction, selectedHazardName, year = 2050 }) => {
    const handleReportClick = () => {
        console.log('PDF button clicked');
        // Track PDF download event
        if (typeof gtag !== 'undefined') {
            gtag('event', 'pdf_download', {
                'event_category': 'interaction',
                'event_label': 'climate_report',
                'regions_count': regions?.length || 0,
                'has_climate_data': climatePrediction?.length > 0,
                'selected_hazard': selectedHazardName || 'none'
            });
        }
    };

    // Only show PDF button if user has selected regions
    const hasSelectedRegions = regions && regions.length > 0;

    return (
        <div>
            <div style={{ textAlign: 'center', padding: '20px', backgroundColor: '#f5f5f5' }}>
                {hasSelectedRegions ? (
                    <PDFDownloadLink
                        document={<ClimateReport 
                            regions={regions} 
                            climatePrediction={climatePrediction} 
                            selectedHazardName={selectedHazardName}
                            year={year}
                        />}
                        fileName="climate-risk-assessment-report.pdf"
                        style={{
                            backgroundColor: '#007bff',
                            color: 'white',
                            padding: '12px 24px',
                            borderRadius: '5px',
                            textDecoration: 'none',
                            fontSize: '16px',
                            fontWeight: 'bold',
                            display: 'inline-block',
                            cursor: 'pointer',
                            border: 'none',
                        }}
                        onClick={handleReportClick}
                    >
                        {({ loading }) =>
                            loading ? 'Generating Report...' : 'Generate Climate Report'
                        }
                    </PDFDownloadLink>
                ) : (
                    <div style={{
                        backgroundColor: '#f0f0f0',
                        color: '#666',
                        padding: '12px 24px',
                        borderRadius: '5px',
                        fontSize: '16px',
                        fontWeight: 'bold',
                        display: 'inline-block',
                        border: '2px dashed #ccc',
                    }}>
                        Select a region to generate report
                    </div>
                )}
            </div>
            <div className="contact-footer">
                <ContactUs />
                <Handbook />
                <AdaptationGuide />
            </div>
            <FooterLogos />
            <FooterText />
        </div>
    );
};

export default Footer;

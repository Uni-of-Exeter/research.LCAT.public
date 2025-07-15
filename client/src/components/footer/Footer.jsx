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

import { pdf } from '@react-pdf/renderer';
import html2canvas from 'html2canvas';
import React, { useState } from "react";

import ClimateReport from "../report/report";
import AdaptationGuide from "./AdaptationGuide";
import ContactUs from "./ContactUs";
import FooterLogos from "./FooterLogos";
import FooterText from "./FooterText";
import Handbook from "./Handbook";

const Footer = ({ regions, climatePrediction, selectedHazardName, year = 2050, climateSummaryRef }) => {
    const [isGenerating, setIsGenerating] = useState(false);

    const captureAndGenerateReport = async () => {
        setIsGenerating(true);
        
        try {
            // Capture the climate summary screenshot
            let climateSummaryImage = null;
            if (climateSummaryRef?.current) {
                const canvas = await html2canvas(climateSummaryRef.current, {
                    backgroundColor: '#ffffff',
                    scale: 2,
                    useCORS: true,
                    allowTaint: true,
                    height: climateSummaryRef.current.offsetHeight,
                    width: climateSummaryRef.current.offsetWidth,
                });
                climateSummaryImage = canvas.toDataURL('image/png');
            }

            // Generate the PDF with the captured image
            const pdfDocument = (
                <ClimateReport 
                    regions={regions} 
                    climatePrediction={climatePrediction} 
                    selectedHazardName={selectedHazardName}
                    year={year}
                    climateSummaryImage={climateSummaryImage}
                />
            );

            const blob = await pdf(pdfDocument).toBlob();
            
            // Create download link
            const url = URL.createObjectURL(blob);
            const link = document.createElement('a');
            link.href = url;
            link.download = 'climate-risk-assessment-report.pdf';
            link.click();
            
            // Clean up
            URL.revokeObjectURL(url);

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
        } catch (error) {
            console.error('Error generating report:', error);
        } finally {
            setIsGenerating(false);
        }
    };

    return (
        <div>
            <div style={{ textAlign: 'center', padding: '20px', backgroundColor: '#f5f5f5' }}>
                <button
                    onClick={captureAndGenerateReport}
                    disabled={isGenerating}
                    style={{
                        backgroundColor: isGenerating ? '#6c757d' : '#007bff',
                        color: 'white',
                        padding: '12px 24px',
                        borderRadius: '5px',
                        fontSize: '16px',
                        fontWeight: 'bold',
                        cursor: isGenerating ? 'not-allowed' : 'pointer',
                        border: 'none',
                        opacity: isGenerating ? 0.7 : 1,
                    }}
                >
                    {isGenerating ? 'Generating Report...' : 'Generate Report'}
                </button>
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

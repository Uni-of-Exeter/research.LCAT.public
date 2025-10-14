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
import React, { useEffect, useState } from "react";

import ClimateReport from "../report/report";
import AdaptationGuide from "./AdaptationGuide";
import ContactUs from "./ContactUs";
import FooterLogos from "./FooterLogos";
import FooterText from "./FooterText";
import Handbook from "./Handbook";
import PageSelectionModal from './PageSelectionModal';

const Footer = ({ regions, climatePrediction, selectedImpactHazard, selectedAdaptationHazards, filterName, rcp, season, applyCoastalFilter }) => {
    const [showPageSelection, setShowPageSelection] = useState(false);
    const [selectedPageIds, setSelectedPageIds] = useState([]);
    const [shouldShowPDF, setShouldShowPDF] = useState(false);
    const [downloadStatus, setDownloadStatus] = useState('idle');
    const [hasDownloaded, setHasDownloaded] = useState(false);
    const [pdfUrl, setPdfUrl] = useState(null);
    const [pdfError, setPdfError] = useState(null);

    const onPageSelection = (pageIds) => {
        setSelectedPageIds(pageIds);
        setShowPageSelection(false);
        setShouldShowPDF(true);
        setDownloadStatus('generating');
        setHasDownloaded(false);
        setPdfUrl(null);
    };

    // Handle PDF generation errors
    useEffect(() => {
        if (pdfError) {
            setDownloadStatus('idle');
            setHasDownloaded(false);
            setPdfError(null);
        }
    }, [pdfError]);

    useEffect(() => {
        if (pdfUrl && downloadStatus === 'generating' && !hasDownloaded) {
            setHasDownloaded(true);

            const link = document.createElement('a');
            link.href = pdfUrl;
            link.download = 'LCAT-report.pdf';
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);

            // Clean up state
            setDownloadStatus('idle');
            setShouldShowPDF(false);
        }
    }, [pdfUrl, downloadStatus, hasDownloaded]);

    const availablePages = [
        {
            id: 'climate',
            title: 'Climate Summary',
            defaultSelected: true,
            available: regions && regions.length > 0
        },
        {
            id: 'hazards',
            title: 'Climate Hazard Risk',
            defaultSelected: true,
            available: true
        },
        {
            id: 'health-impacts',
            title: 'Health Impacts',
            defaultSelected: true,
            available: selectedImpactHazard
        },
        {
            id: 'community-impacts',
            title: 'Community Impacts',
            defaultSelected: true,
            available: selectedImpactHazard
        },
        {
            id: 'vulnerability',
            title: 'Vulnerabilities',
            defaultSelected: true,
            available: true
        },
        {
            id: 'adaptations',
            title: 'Adaptations',
            defaultSelected: true,
            available: true
        },
    ].filter(page => page.available);

    const handleReportClick = () => {
        setShowPageSelection(true);
        // Track PDF download event
        if (typeof gtag !== 'undefined') {
            gtag('event', 'pdf_download', {
                'event_category': 'interaction',
                'event_label': 'climate_report',
                'regions_count': regions?.length || 0,
                'has_climate_data': climatePrediction?.length > 0,
                'selected_hazard': selectedImpactHazard || 'none',
                'rcp': rcp || 'none',
                'season': season || 'none'
            });
        }
    };

    // Only show PDF button if user has selected regions
    const hasSelectedRegions = regions && regions.length > 0;

    return (
        <div>
            <div className="pdf-generation-section">
                {hasSelectedRegions ? (
                    <>
                        <div className="pdf-button-container">
                            <button
                                onClick={handleReportClick}
                                className="generate-report-button"
                            >
                                Generate Climate Report
                            </button>
                            <div className={`generating-status ${downloadStatus === 'generating' ? 'visible' : 'hidden'}`}>
                                {downloadStatus === 'generating' ? 'Generating report...' : ''}
                            </div>
                        </div>
                        
                        {shouldShowPDF && selectedPageIds.length > 0 && (
                            <PDFDownloadLink
                                document={<ClimateReport 
                                    regions={regions} 
                                    climatePrediction={climatePrediction} 
                                    selectedImpactHazard={selectedImpactHazard}
                                    selectedAdaptationHazards={selectedAdaptationHazards}
                                    filterName={filterName}
                                    rcp={rcp}
                                    season={season}
                                    applyCoastalFilter={applyCoastalFilter}
                                    selectedPages={selectedPageIds}
                                />}
                                fileName="LCAT-report.pdf"
                                className="pdf-download-link"
                            >
                                {({ url, error }) => {
                                    if (error && !pdfError) {
                                        setPdfError(error);
                                    }
                                    
                                    if (url && !pdfUrl) {
                                        setPdfUrl(url);
                                    }
                                    
                                    return null;
                                }}
                            </PDFDownloadLink>
                        )}
                    </>
                ) : (
                        <div className="select-region-prompt">
                        Select a region to generate report
                    </div>
                )}
            </div>

            <PageSelectionModal
                isOpen={showPageSelection}
                onClose={() => setShowPageSelection(false)}
                onGenerate={onPageSelection}
                availablePages={availablePages}
            />
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

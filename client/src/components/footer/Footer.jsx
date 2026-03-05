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

import { usePDF } from '@react-pdf/renderer';
import React, { useEffect, useRef, useState } from "react";

import ClimateReport from "../report/report";
import AdaptationGuide from "./AdaptationGuide";
import ContactUs from "./ContactUs";
import FooterLogos from "./FooterLogos";
import FooterText from "./FooterText";
import Handbook from "./Handbook";
import PageSelectionModal from './PageSelectionModal';

// Generates a PDF and renders the appropriate status/download link.
// Rendered conditionally by Footer — mounting starts generation, unmounting cancels any pending reset timer.
const PdfDownloader = ({ document, fileName, onDone }) => {
    const [instance] = usePDF({ document });
    const timerRef = useRef(null);

    useEffect(() => {
        return () => {
            // If a new generation starts before the timer fires, cancel the deferred reset
            if (timerRef.current) clearTimeout(timerRef.current);
        };
    }, []);

    const handleClick = () => {
        const urlToRevoke = instance.url;
        // Defer unmount so the browser can initiate the download first
        timerRef.current = setTimeout(() => {
            URL.revokeObjectURL(urlToRevoke);
            onDone();
            timerRef.current = null;
        }, 1000);
    };

    if (instance.loading) return <span className="generating-status visible">Generating report...</span>;
    if (instance.error) return <span className="generating-status visible">Download failed — please try again.</span>;
    if (instance.url) return <a href={instance.url} download={fileName} onClick={handleClick}>Download your report</a>;
    return null;
};

const Footer = ({ regions, climatePrediction, selectedImpactHazard, selectedAdaptationHazards, filterName, rcp, season, applyCoastalFilter }) => {
    // Generate filename with region names
    const regionNames = regions && regions.length > 0
        ? regions.map(r => r.name.replace(/'/g, '').replace(/[^a-zA-Z0-9]+/g, '-').replace(/^-|-$/g, '')).join('_')
        : 'no-region';
    const reportFileName = `LCAT-summary-report-${regionNames}.pdf`;

    const [showPageSelection, setShowPageSelection] = useState(false);
    const [selectedPageIds, setSelectedPageIds] = useState([]);
    const [shouldShowPDF, setShouldShowPDF] = useState(false);
    const [generationId, setGenerationId] = useState(0);

    const onPageSelection = (pageIds) => {
        setSelectedPageIds(pageIds);
        setShowPageSelection(false);
        setShouldShowPDF(true);
        setGenerationId(id => id + 1); // changing key unmounts the old PdfDownloader, cancelling any pending timer
    };

    const availablePages = [
        {
            id: 'climate',
            title: 'Climate Summary',
            defaultSelected: true,
        },
        {
            id: 'hazards',
            title: 'Climate Hazard Risk',
            defaultSelected: true,
        },
        {
            id: 'health-impacts',
            title: 'Health Impacts',
            defaultSelected: true,
        },
        {
            id: 'community-impacts',
            title: 'Community Impacts',
            defaultSelected: true,
        },
        {
            id: 'vulnerability',
            title: 'Vulnerabilities',
            defaultSelected: true,
        },
        {
            id: 'adaptations',
            title: 'Adaptations',
            defaultSelected: true,
        },
    ];

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
            <div id="generate-report-section">
                {hasSelectedRegions ? (
                    <>
                        <div className="pdf-button-container">
                            <button
                                onClick={handleReportClick}
                                className="generate-report-button"
                            >
                                Generate LCAT Summary Report
                            </button>
                            {shouldShowPDF && selectedPageIds.length > 0 && (
                                <PdfDownloader
                                    key={generationId}
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
                                    fileName={reportFileName}
                                    onDone={() => setShouldShowPDF(false)}
                                />
                            )}
                        </div>
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

import "./PageSelectionModal.css";

import { useState } from "react";

const PageSelectionModal = ({ isOpen, onClose, onGenerate, availablePages }) => {
    const [selectedPages, setSelectedPages] = useState(
        availablePages.reduce((acc, page) => ({ ...acc, [page.id]: page.defaultSelected }), {}),
    );

    const handlePageToggle = (pageId) => {
        setSelectedPages((prev) => ({
            ...prev,
            [pageId]: !prev[pageId],
        }));
    };

    const handleGenerate = () => {
        const selectedPageIds = Object.keys(selectedPages).filter((id) => selectedPages[id]);
        onGenerate(selectedPageIds);
        onClose();
    };

    const handleKeyDown = (event) => {
        if (event.key === "Escape") {
            onClose();
        }
    };

    const handleOverlayClick = (event) => {
        // Only close if clicking the overlay itself, not its children
        if (event.target === event.currentTarget) {
            onClose();
        }
    };

    const selectedCount = Object.values(selectedPages).filter(Boolean).length;

    if (!isOpen) return null;

    return (
        <div
            className="modal-overlay"
            onClick={handleOverlayClick}
            onKeyDown={handleKeyDown}
            role="button"
            aria-label="Close modal (click background or press Escape)"
            tabIndex="0"
        >
            <div className="modal-content">
                <h3 id="modal-title">Select Report Pages</h3>

                <div className="page-options">
                    {availablePages.map((page) => (
                        <label key={page.id} className="page-option">
                            <input
                                type="checkbox"
                                checked={selectedPages[page.id]}
                                onChange={() => handlePageToggle(page.id)}
                                aria-label={`Include ${page.title} in report`}
                            />
                            <div className="page-info">
                                <span className="page-name">{page.title}</span>
                            </div>
                        </label>
                    ))}
                </div>

                <div className="modal-actions">
                    <button onClick={onClose} className="btn-secondary">
                        Cancel
                    </button>
                    <button onClick={handleGenerate} className="btn-primary" disabled={selectedCount === 0}>
                        Generate Report <br />({selectedCount} page{selectedCount !== 1 ? "s" : ""})
                    </button>
                </div>
            </div>
        </div>
    );
};

export default PageSelectionModal;

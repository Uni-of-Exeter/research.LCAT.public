import "./PageSelectionModal.css";

import { useEffect, useRef, useState } from "react";

const PageSelectionModal = ({ isOpen, onClose, onGenerate, availablePages }) => {
    const [selectedPages, setSelectedPages] = useState(
        availablePages.reduce((acc, page) => ({ ...acc, [page.id]: page.defaultSelected }), {}),
    );
    const modalRef = useRef(null);
    const previouslyFocused = useRef(null);

    useEffect(() => {
        if (!isOpen) return;

        previouslyFocused.current = document.activeElement;
        modalRef.current?.focus();

        const previousOverflow = document.body.style.overflow;
        document.body.style.overflow = "hidden";

        function onKeyDown(event) {
            if (event.key === "Escape") {
                onClose();
                return;
            }
            if (event.key === "Tab") {
                const focusable = modalRef.current.querySelectorAll(
                    'button:not([disabled]), [href], input:not([disabled]), select, textarea, [tabindex]:not([tabindex="-1"])',
                );
                if (focusable.length === 0) return;
                const first = focusable[0];
                const last = focusable[focusable.length - 1];
                if (event.shiftKey && document.activeElement === first) {
                    event.preventDefault();
                    last.focus();
                } else if (!event.shiftKey && document.activeElement === last) {
                    event.preventDefault();
                    first.focus();
                }
            }
        }

        window.addEventListener("keydown", onKeyDown);
        return () => {
            window.removeEventListener("keydown", onKeyDown);
            document.body.style.overflow = previousOverflow;
            previouslyFocused.current?.focus?.();
        };
    }, [isOpen, onClose]);

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

    const handleOverlayClick = (event) => {
        // Only close if clicking the overlay itself, not its children
        if (event.target === event.currentTarget) {
            onClose();
        }
    };

    const selectedCount = Object.values(selectedPages).filter(Boolean).length;

    if (!isOpen) return null;

    return (
        /* eslint-disable-next-line jsx-a11y/click-events-have-key-events, jsx-a11y/no-static-element-interactions --
            Backdrop click-to-close is a mouse/touch convenience only; keyboard users close via Escape,
            handled in the useEffect above. This div is intentionally non-interactive/non-focusable. */
        <div className="modal-overlay" onClick={handleOverlayClick}>
            <div
                className="modal-content"
                role="dialog"
                aria-modal="true"
                aria-labelledby="modal-title"
                tabIndex={-1}
                ref={modalRef}
            >
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
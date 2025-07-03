import { useEffect } from "react";

export default function CookiePolicyModal({ open, onClose }) {
    useEffect(() => {
        if (!open) return;
        function onKeyDown(e) {
            if (e.key === 'Escape') onClose();
        }
        window.addEventListener('keydown', onKeyDown);
        return () => window.removeEventListener('keydown', onKeyDown);
    }, [open, onClose]);

    if (!open) return null;

    return (
        <div
            id="cookie-policy-modal"
            role="dialog"
            aria-modal="true"
            tabIndex={-1}
            style={{
                position: "fixed",
                top: 0,
                left: 0,
                width: "100vw",
                height: "100vh",
                background: "rgba(0,0,0,0.4)",
                zIndex: 10001,
                display: "flex",
                alignItems: "center",
                justifyContent: "center"
            }}
        >
            <div
                role="button"
                aria-label="Close cookie policy overlay"
                style={{
                    position: "fixed",
                    top: 0,
                    left: 0,
                    width: "100vw",
                    height: "100vh",
                    background: "transparent",
                    zIndex: 10001,
                    cursor: "pointer"
                }}
                tabIndex={0}
                onClick={onClose}
                onKeyDown={e => {
                    if (e.key === "Enter" || e.key === " ") {
                        e.preventDefault();
                        onClose();
                    }
                }}
            />
            <div
                style={{
                    background: "#fff",
                    borderRadius: 8,
                    maxWidth: 480,
                    width: "90%",
                    maxHeight: "90vh",
                    padding: "2em 1.5em 1.5em 1.5em",
                    boxShadow: "0 4px 24px rgba(0,0,0,0.18)",
                    position: "relative",
                    zIndex: 10002,
                    overflowY: "auto",
                    display: "flex",
                    flexDirection: "column"
                }}
            >
                <button
                    aria-label="Close cookie policy"
                    onClick={onClose}
                    style={{
                        position: "absolute",
                        top: 12,
                        right: 12,
                        background: "none",
                        border: "none",
                        fontSize: 24,
                        color: "#888",
                        cursor: "pointer",
                        zIndex: 10003
                    }}
                >&times;</button>
                <h2 style={{marginTop: 0}}>Cookie Policy</h2>
                <div style={{fontSize: "1rem", lineHeight: 1.6}}>
                    <p><strong>What are cookies?</strong> Cookies are small text files stored on your device to help websites function and collect information about your usage.</p>
                    <p><strong>How we use cookies:</strong> We use essential cookies for site functionality and, with your consent, analytics cookies to understand how visitors use our site. Analytics cookies are only set if you accept them.</p>
                    <p><strong>Essential cookies:</strong> We use a cookie named <code>cookie_consent</code> in your browser&apos;s local storage to remember your cookie preferences, so we do not repeatedly ask for your consent. This value does not expire automatically and will remain until you clear your browser storage or change your preference.</p>
                    <p><strong>Third-party cookies:</strong> We use Google Analytics to collect anonymous usage statistics. For more information, see <a href="https://policies.google.com/technologies/cookies" target="_blank" rel="noopener noreferrer">Google's cookie policy</a>.</p>
                    <p><strong>Managing cookies:</strong> You can accept or reject analytics cookies at any time using the cookie banner or the &quot;Manage cookies&quot; link in the site footer.</p>
                </div>
            </div>
        </div>
    );
}

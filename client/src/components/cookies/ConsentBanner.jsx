import { useEffect, useState } from "react";

import CookiePolicyModal from "./PolicyModal";

const GA_MEASUREMENT_ID = "G-RLE3Q1KGJJ";

function loadGAScript() {
    if (window.gtag) return;
    const script = document.createElement("script");
    script.src = `https://www.googletagmanager.com/gtag/js?id=${GA_MEASUREMENT_ID}`;
    script.async = true;
    document.head.appendChild(script);

    window.dataLayer = window.dataLayer || [];
    function gtag(){window.dataLayer.push(arguments);}
    window.gtag = gtag;
    gtag("js", new Date());
    gtag("config", GA_MEASUREMENT_ID, { 'anonymize_ip': true });
}

export default function CookieConsent() {
    const [show, setShow] = useState(false);
    const [showPolicy, setShowPolicy] = useState(false);

    useEffect(() => {
        const consent = localStorage.getItem("cookie_consent");
        // Only load the GA script if consent is explicitly given
        if (consent === "true") {
            loadGAScript();
        } else if (consent === null) {
            setShow(true);
        }
        const handler = () => setShow(true);
        window.addEventListener('open_cookie_banner', handler);
        return () => window.removeEventListener('open_cookie_banner', handler);
    }, []);

    useEffect(() => {
        if (!showPolicy) return;
        function onKeyDown(e) {
            if (e.key === 'Escape') setShowPolicy(false);
        }
        window.addEventListener('keydown', onKeyDown);
        return () => window.removeEventListener('keydown', onKeyDown);
    }, [showPolicy]);

    const accept = () => {
        localStorage.setItem("cookie_consent", "true");
        loadGAScript();
        setShow(false);
    };

    const decline = () => {
        localStorage.setItem("cookie_consent", "false");
        setShow(false);
    };

    if (!show) return null;

    return (
        <>
            <div style={{
                position: "fixed",
                bottom: 0,
                left: 0,
                right: 0,
                background: "#fffbe7",
                borderTop: "1px solid #ccc",
                padding: "1em",
                zIndex: 10000,
                textAlign: "center"
            }}>
                We use cookies to improve your experience and to understand how people use our site. You can accept or reject non-essential cookies. For more information, see our {" "}
                <button
                    style={{
                        background: "none",
                        border: "none",
                        color: "#0071c1",
                        textDecoration: "underline",
                        cursor: "pointer",
                        padding: 0,
                        font: "inherit"
                    }}
                    onClick={() => setShowPolicy(true)}
                    aria-haspopup="dialog"
                    aria-controls="cookie-policy-modal"
                >
                    Cookie Policy
                </button>.
                <div style={{ marginTop: "0.5em" }}>
                    <button
                        onClick={accept}
                        style={{marginRight: 20}}
                    >
                        Accept all cookies
                    </button>
                    <button onClick={decline}>Reject non-essential cookies</button>
                </div>
            </div>
            <CookiePolicyModal open={showPolicy} onClose={() => setShowPolicy(false)} />
        </>
    );
}

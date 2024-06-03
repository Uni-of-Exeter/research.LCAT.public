import React from "react";

const ContactUs = () => {
    return (
        <div className="footer-flex-container">
            <h1>Need help? Contact us.</h1>
            <div className="footer-flex-content">
                <p>
                    <a className="email-button" href="mailto:lcat@exeter.ac.uk" target="_blank" rel="noreferrer"></a>
                </p>
                <p>
                    Email us at:&nbsp;
                    <a href="mailto:lcat@exeter.ac.uk" target="_blank" rel="noreferrer">
                        lcat@exeter.ac.uk
                    </a>
                </p>
            </div>
        </div>
    );
};

export default ContactUs;

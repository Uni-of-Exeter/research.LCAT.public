import ContactUs from "./ContactUs";
import FooterLogos from "./FooterLogos";
import FooterText from "./FooterText";
import UserGuide from "./UserGuide";
import AdaptationGuide from "./AdaptationGuide";

import "./Footer.css";

function Footer() {
    return (
        <div>
            <div className="contact-footer">
                <ContactUs />
                <UserGuide />
                <AdaptationGuide />
            </div>
            <FooterLogos />
            <FooterText />
        </div>
    );
}

export default Footer;

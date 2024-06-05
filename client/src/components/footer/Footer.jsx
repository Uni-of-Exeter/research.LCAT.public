/* Development before 2024 Copyright (C) Then Try This and University of Exeter
Development from 2024 Copyright (C) University of Exeter

This program is free software: you can redistribute it and/or modify
it under the terms of the Common Good Public License Beta 1.0 as
published at http://www.cgpl.org

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
Common Good Public License Beta 1.0 for more details. */

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

import { ReactComponent as LCATLogoSvg } from "../../images/logos/LCAT_Logo_Primary_RGB.svg";

function LCATHeader() {
    return (
        <div className="white-section">
            <header className="App-header">
                <LCATLogoSvg width={300} />
            </header>
        </div>
    );
}

export default LCATHeader;

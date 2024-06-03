import SvgHealthConditions from "../../images/personalSocialVulnerabilities/HealthConditions.jsx";
import SvgLowIncomes from "../../images/personalSocialVulnerabilities/LowIncomes.jsx";
import SvgLowLocalKnowledge from "../../images/personalSocialVulnerabilities/LowLocalKnowledge.jsx";
import SvgLowMobility from "../../images/personalSocialVulnerabilities/LowMobility.jsx";
import SvgOlderPeople from "../../images/personalSocialVulnerabilities/OlderPeople.jsx";
import SvgPrivateSocialHousing from "../../images/personalSocialVulnerabilities/PrivateSocialHousing.jsx";
import SvgSociallyIsolated from "../../images/personalSocialVulnerabilities/SociallyIsolated.jsx";
import SvgUnderFives from "../../images/personalSocialVulnerabilities/UnderFives.jsx";

// This map contains the rendered content in the PersonalSocialVulnerabilities component
export const vulnerabilityData = [
    {
        name: "Older people",
        icon: <SvgOlderPeople className="vulnerability-img" />,
        details: (
            <div>
                <p>
                    <strong className="vulnerability-emphasis">Who? </strong>Older people over 65, but particularly over
                    75
                </p>
                <p>
                    <strong className="vulnerability-emphasis">Why are they vulnerable?</strong>
                </p>
                <ul>
                    <li>
                        <strong>Physical sensitivity:</strong>
                        <ul>
                            <li>
                                Older people are more biophysically sensitive to climate impacts such as finding it
                                harder to regulate temperatures during extreme heat, particularly if they have other
                                health conditions such as chronic cardiovascular disease.
                            </li>
                            <li>
                                Older people are more likely to have other physical vulnerabilities such as poor health
                                or low mobility. This means that some older people are unable to respond or adapt to a
                                changing climate or weather event due to being bed-bound, reliant on caregivers or
                                living with degenerative illnesses such as dementia.
                            </li>
                        </ul>
                    </li>
                    <li>
                        <strong>Compounding vulnerabilities:</strong>
                        <ul>
                            <li>
                                Older people (over 65 and esp. over 75) are the age group associated with multiple
                                compounding vulnerabilities such as social isolation and living in certain types of
                                housing that might increase their overall vulnerability.
                            </li>
                        </ul>
                    </li>
                </ul>
                <p>
                    <strong className="vulnerability-emphasis">How can I find more information?</strong>
                </p>
                <ul>
                    <li>
                        Climate Just's insight & advice:{" "}
                        <a href="https://climatejust.org.uk/messages/older-people" target="_blank" rel="noreferrer">
                            Older people | Climate Just
                        </a>
                    </li>
                </ul>
                <p>
                    <strong className="vulnerability-emphasis">How can I find local data?</strong>
                </p>
                <ul>
                    <li>
                        Climate Just's mapping tool:{" "}
                        <a href="https://www.climatejust.org.uk/map" target="_blank" rel="noreferrer">
                            Mapping tool page | Climate Just
                        </a>
                    </li>
                </ul>
            </div>
        ),
    },
    {
        name: "Under 5s",
        icon: <SvgUnderFives className="vulnerability-img" />,
        details: (
            <div>
                <p>
                    <strong className="vulnerability-emphasis">Who? </strong>Very young children & babies (under 5s)
                </p>
                <p>
                    <strong className="vulnerability-emphasis">Why are they vulnerable?</strong>
                </p>
                <ul>
                    <li>
                        <strong>Physical sensitivity:</strong>
                        <ul>
                            <li>Under 5s are less able to regulate their own temperatures in high heats.</li>
                            <li>
                                Under 5s are reliant on their care givers to support them to adapt to hazards or
                                temperature changes, for example.
                            </li>
                            <li>
                                Under 5s are more susceptible to mental health issues caused by the trauma of extreme
                                events such as flooding.
                            </li>
                        </ul>
                    </li>
                </ul>
                <p>
                    <strong className="vulnerability-emphasis">How can I find more information?</strong>
                </p>
                <ul>
                    <li>
                        Climate Just's insight & advice:{" "}
                        <a
                            href="https://climatejust.org.uk/messages/young-children-and-babies"
                            target="_blank"
                            rel="noreferrer"
                        >
                            Young children and babies | Climate Just
                        </a>
                    </li>
                </ul>
                <p>
                    <strong className="vulnerability-emphasis">How can I find local data?</strong>
                </p>
                <ul>
                    <li>
                        Climate Just's mapping tool:{" "}
                        <a href="https://www.climatejust.org.uk/map" target="_blank" rel="noreferrer">
                            Mapping tool page | Climate Just
                        </a>
                    </li>
                </ul>
            </div>
        ),
    },
    {
        name: "People with health conditions",
        icon: <SvgHealthConditions className="vulnerability-img" />,
        details: (
            <div>
                <p>
                    <strong className="vulnerability-emphasis">Who? </strong>People with health conditions/in poor
                    health/with existing physical and mental illness
                </p>
                <p>
                    <strong className="vulnerability-emphasis">Why are they vulnerable?</strong>
                </p>
                <p>
                    Health conditions and disabilities are diverse and different and so impact and harm will differ
                    depending on the condition(s). As such there are multiple reasons as to why people with health
                    conditions can be more vulnerable including, but not limited to:
                </p>
                <ul>
                    <li>Health conditions being exacerbated or worsened by climate change.</li>
                    <li>
                        Physical limitations and/or limited mobility impacting people's ability to adapt, prepare or
                        respond to changing climate and weather events.
                    </li>
                    <li>Mental health conditions affecting people's ability to adapt or cope.</li>
                    <li>Particular medications reducing people's physical ability to cope.</li>
                    <li>Being reliant on carers to help them adapt, respond and recover.</li>
                    <li>
                        Extreme events, such as flooding, limiting people's access to vital healthcare, carers or
                        medication.
                    </li>
                    <li>
                        Compounding vulnerabilities associated with poor health / disability such as being socially
                        isolated, on a low income, or being at a vulnerable age.
                    </li>
                </ul>
                <p>
                    <strong className="vulnerability-emphasis">How can I find more information?</strong>
                </p>
                <ul>
                    <li>
                        Climate Just's insight & advice:{" "}
                        <a
                            href="https://climatejust.org.uk/messages/people-poor-health"
                            target="_blank"
                            rel="noreferrer"
                        >
                            People in poor health | Climate Just
                        </a>
                    </li>
                </ul>
                <p>
                    <strong className="vulnerability-emphasis">How can I find local data?</strong>
                </p>
                <ul>
                    <li>
                        Climate Just's mapping tool:{" "}
                        <a href="https://www.climatejust.org.uk/map" target="_blank" rel="noreferrer">
                            Mapping tool page | Climate Just
                        </a>
                    </li>
                </ul>
            </div>
        ),
    },
    {
        name: "People on low incomes",
        icon: <SvgLowIncomes className="vulnerability-img" />,
        details: (
            <div>
                <p>
                    <strong className="vulnerability-emphasis">Who? </strong>People on low incomes
                </p>
                <p>
                    <strong className="vulnerability-emphasis">Why are they vulnerable?</strong>
                </p>
                <ul>
                    <li>
                        Less financial means by which to prepare for, respond to and recover from a changing climate and
                        extreme weather events such as being able to afford adaptations to their home or take out
                        affordable home insurance.
                    </li>
                    <li>
                        Poverty is associated with multiple other vulnerabilities such as being in ill-health or having
                        a disability which means those on low incomes are a particularly high-risk group.
                    </li>
                    <li>
                        More likely to be renting a property meaning they don't have the power to make changes or
                        adaptations to that home.
                    </li>
                    <li>
                        More likely to live in properties that are less resilient to flooding (such as caravans) and
                        more exposed to extreme heat (such as poorly ventilated and insulated social housing blocks).
                    </li>
                    <li>
                        Transport to get to work and school can be more disrupted during an extreme weather event as
                        those on low incomes are more likely to rely on public transport.
                    </li>
                    <li>Less likely to seek help or be involved in political processes giving them a voice.</li>
                </ul>
                <p>
                    <strong className="vulnerability-emphasis">How can I find more information?</strong>
                </p>
                <ul>
                    <li>
                        Climate Just's insight & advice:{" "}
                        <a
                            href="https://climatejust.org.uk/messages/people-low-incomes"
                            target="_blank"
                            rel="noreferrer"
                        >
                            People on low incomes | Climate Just
                        </a>
                    </li>
                </ul>
                <p>
                    <strong className="vulnerability-emphasis">How can I find local data?</strong>
                </p>
                <ul>
                    <li>
                        Climate Just's mapping tool:{" "}
                        <a href="https://www.climatejust.org.uk/map" target="_blank" rel="noreferrer">
                            Mapping tool page | Climate Just
                        </a>
                    </li>
                </ul>
            </div>
        ),
    },
    {
        name: "Tenants in private or social housing",
        icon: <SvgPrivateSocialHousing className="vulnerability-img" />,
        details: (
            <div>
                <p>
                    <strong className="vulnerability-emphasis">Who? </strong>Tenants in private or social housing
                </p>
                <p>
                    <strong className="vulnerability-emphasis">Why are they vulnerable?</strong>
                </p>
                <ul>
                    <li>
                        More likely to be on a low income. This compounds their vulnerability but also means being less
                        able to pay for adaptations or fix/ replace goods damaged by an extreme weather event and;
                    </li>
                    <li>Less likely to have taken out contents insurance to cover loss and damage during a flood.</li>
                    <li>
                        They are reliant on a landlord to have taken out buildings insurance and to make adaptations to
                        the building and are often restricted as to modifications or changes they are allowed to make to
                        a rental property themselves.
                    </li>
                    <li>
                        Private tenancy is associated with shorter residency in an area, meaning less local knowledge to
                        support them to understand local risk and then access support networks/ systems in times of
                        extreme weather events.
                    </li>
                    <li>More likely to live in "purpose-built" flats which can be more vulnerable to extreme heat.</li>
                    <li>
                        More likely to live in overcrowded homes impacting ventilation and rising the internal
                        temperatures during times of high/ extreme heat.
                    </li>
                </ul>
                <p>
                    <strong className="vulnerability-emphasis">How can I find more information?</strong>
                </p>
                <ul>
                    <li>
                        Climate Just's insight & advice:{" "}
                        <a
                            href="https://climatejust.org.uk/messages/tenants-social-or-private-rented-housing"
                            target="_blank"
                            rel="noreferrer"
                        >
                            Tenants in social or private rented housing | Climate Just
                        </a>{" "}
                        and{"  "}
                        <a
                            href="https://climatejust.org.uk/messages/adapting-buildings"
                            target="_blank"
                            rel="noreferrer"
                        >
                            Adapting buildings | Climate Just
                        </a>
                    </li>
                </ul>
                <p>
                    <strong className="vulnerability-emphasis">How can I find local data?</strong>
                </p>
                <ul>
                    <li>
                        Climate Just's mapping tool:{" "}
                        <a href="https://www.climatejust.org.uk/map" target="_blank" rel="noreferrer">
                            Mapping tool page | Climate Just
                        </a>
                    </li>
                </ul>
            </div>
        ),
    },
    {
        name: "People living in area for a short time",
        icon: <SvgLowLocalKnowledge className="vulnerability-img" />,
        details: (
            <div>
                <p>
                    <strong className="vulnerability-emphasis">Who? </strong>People who have lived in an area for a
                    short time/areas with highly transient populations
                </p>
                <p>
                    <strong className="vulnerability-emphasis">Why are they vulnerable?</strong>
                </p>
                <ul>
                    <li>
                        Lack local knowledge about:
                        <ul>
                            <li>Localised risks (e.g flood risk)</li>
                            <li>Local support structure and services</li>
                            <li>How to take action during an extreme weather event</li>
                        </ul>
                    </li>
                    <li>Lack of social networks and support structures.</li>
                    <li>
                        Areas with high rates of population transience are associated with compounding vulnerability
                        factors such as poor-quality housing, insecure, low-paid work and physical and social isolation.
                    </li>
                    <li>
                        For people who have come from other countries, low or no English proficiency may impact people's
                        understanding of, and access to, local information on climate impacts.
                    </li>
                </ul>
                <p>
                    <strong className="vulnerability-emphasis">How can I find more information?</strong>
                </p>
                <ul>
                    <li>
                        Climate Just's insight & advice:{" "}
                        <a
                            href="https://climatejust.org.uk/messages/people-who-have-lived-area-short-time"
                            target="_blank"
                            rel="noreferrer"
                        >
                            People who have lived in an area for a short time | Climate Just
                        </a>
                    </li>
                </ul>
                <p>
                    <strong className="vulnerability-emphasis">How can I find local data?</strong>
                </p>
                <ul>
                    <li>
                        Climate Just's mapping tool provides a range of data including length of residency & English
                        proficiency:{" "}
                        <a href="https://www.climatejust.org.uk/map" target="_blank" rel="noreferrer">
                            Mapping tool page | Climate Just
                        </a>
                    </li>
                </ul>
            </div>
        ),
    },
    {
        name: "People who are socially isolated",
        icon: <SvgSociallyIsolated className="vulnerability-img" />,
        details: (
            <div>
                <p>
                    <strong className="vulnerability-emphasis">Who? </strong>People who are socially isolated
                </p>
                <p>This can include, but is not limited to:</p>
                <ul>
                    <li>Single pensioner households.</li>
                    <li>People with pre-school age children.</li>
                    <li>Transient populations with little access to friends and family.</li>
                </ul>
                <p>
                    <strong className="vulnerability-emphasis">Why are they vulnerable?</strong>
                </p>
                <ul>
                    <li>
                        Lack of support networks to alert them to an extreme event, support them to respond and support
                        them to recover.
                    </li>
                    <li>
                        More likely to be unknown by community and local services making them hard to identify and help.
                    </li>
                    <li>Less likely to know about, and access, community support.</li>
                    <li>
                        Social isolation is associated with compounding vulnerabilities raising overall risk. These can
                        include old age, poverty and poor health. Social isolation is particularly high for single
                        pensioner households and those isolated with dependent children face practical difficulties in
                        responding to an extreme weather event due to lack of support networks.
                    </li>
                    <li>Social isolation, coupled with rural/ coastal isolation, can exacerbate vulnerability.</li>
                </ul>
                <p>
                    <strong className="vulnerability-emphasis">How can I find more information?</strong>
                </p>
                <ul>
                    <li>
                        Climate Just's insight & advice:{" "}
                        <a
                            href="https://climatejust.org.uk/messages/people-who-are-socially-isolated"
                            target="_blank"
                            rel="noreferrer"
                        >
                            People who are socially isolated | Climate Just
                        </a>
                    </li>
                </ul>
                <p>
                    <strong className="vulnerability-emphasis">How can I find local data?</strong>
                </p>
                <ul>
                    <li>
                        Climate Just's mapping tool:{" "}
                        <a href="https://www.climatejust.org.uk/map" target="_blank" rel="noreferrer">
                            Mapping tool page | Climate Just
                        </a>
                    </li>
                </ul>
            </div>
        ),
    },
    {
        name: "People with low personal mobility",
        icon: <SvgLowMobility className="vulnerability-img" />,
        details: (
            <div>
                <p>
                    <strong className="vulnerability-emphasis">Who? </strong>Those with low personal mobility & low
                    access to services
                </p>
                <p>
                    <strong className="vulnerability-emphasis">Why are they vulnerable?</strong>
                </p>
                <ul>
                    <li>
                        <strong>Low personal mobility:</strong>
                        <ul>
                            <li>May not be able to respond quickly during an extreme weather event.</li>
                            <li>
                                More reliant on care givers or support network to help them. This support network could
                                be reduced during extreme weather events.
                            </li>
                            <li>
                                Services, support and equipment that usually support people may be affected, or even
                                stopped during extreme weather events.
                            </li>
                            <li>
                                May have associated vulnerabilities which makes them more vulnerable overall such as
                                those related to poor health or age.
                            </li>
                        </ul>
                    </li>
                    <li>
                        <strong>Low access to services:</strong>
                        <ul>
                            <li>
                                Some rural and coastal areas lack access to services needed during an extreme weather
                                event, making getting help even harder, particularly if that infrastructure is disrupted
                                by the weather event.
                            </li>
                            <li>
                                Some rural and coastal areas have higher proportions of communities facing multiple
                                vulnerabilities such as those on a low income, those reliant on seasonal and low-paid
                                work, older communities and transient communities increasing overall vulnerability.
                            </li>
                            <li>
                                Extreme weather events can reduce people's mobility by cutting off or disrupting
                                transport infrastructure making it harder for communities affected to get help and help
                                themselves.
                            </li>
                        </ul>
                    </li>
                </ul>
                <p>
                    <strong className="vulnerability-emphasis">How can I find more information?</strong>
                </p>
                <ul>
                    <li>
                        Climate Just's insight & advice, ensuring principles of social justice are included in
                        adaptation planning:{" "}
                        <a
                            href="https://climatejust.org.uk/messages/people-low-personal-mobility"
                            target="_blank"
                            rel="noreferrer"
                        >
                            People with low personal mobility | Climate Just
                        </a>
                    </li>
                </ul>
                <p>
                    <strong className="vulnerability-emphasis">How can I find local data?</strong>
                </p>
                <ul>
                    <li>
                        Climate Just's mapping tool:{" "}
                        <a href="https://www.climatejust.org.uk/map" target="_blank" rel="noreferrer">
                            Mapping tool page | Climate Just
                        </a>
                    </li>
                </ul>
            </div>
        ),
    },
];

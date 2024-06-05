/* Development before 2024 Copyright (C) Then Try This and University of Exeter
Development from 2024 Copyright (C) University of Exeter

This program is free software: you can redistribute it and/or modify
it under the terms of the Common Good Public License Beta 1.0 as
published at http://www.cgpl.org

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
Common Good Public License Beta 1.0 for more details. */

export function decileToNumber(decile) {
    if (decile=="dec_1") return 0;
    if (decile=="dec_2") return 1;
    if (decile=="dec_3") return 2;
    if (decile=="dec_4") return 3;
    if (decile=="dec_5") return 4;
    if (decile=="dec_6") return 5;
    if (decile=="dec_7") return 6;
    if (decile=="dec_8") return 7;
    return 8;
}

export function flipDecile(decile) {
    if (decile=="dec_1") return "dec_9";
    if (decile=="dec_2") return "dec_8";
    if (decile=="dec_3") return "dec_7";
    if (decile=="dec_4") return "dec_6";
    if (decile=="dec_5") return "dec_5";
    if (decile=="dec_6") return "dec_4";
    if (decile=="dec_7") return "dec_3";
    if (decile=="dec_8") return "dec_2";
    return "dec_1";
}

export function decileToText(decile) {
    if (decile=="dec_1") return "10%";
    if (decile=="dec_2") return "20%";
    if (decile=="dec_3") return "30%";
    if (decile=="dec_4") return "40%";
    if (decile=="dec_5") return "50%";
    if (decile=="dec_6") return "60%";
    if (decile=="dec_7") return "70%";
    if (decile=="dec_8") return "80%";
    return "90%";
}



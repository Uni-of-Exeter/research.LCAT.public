/* Development before 2024 Copyright (C) Then Try This and University of Exeter
Development from 2024 Copyright (C) University of Exeter

This program is free software: you can redistribute it and/or modify
it under the terms of the Common Good Public License Beta 1.0 as
published at http://www.cgpl.org

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
Common Good Public License Beta 1.0 for more details. */

export function andify(a) {
    if (a.length<2) {
        return a[0];
    } else {
        return a.slice(0, -1).join(', ')+' and '+a.slice(-1);
    }
}

export function formatTextWrap(text, maxLineLength) {
    const words = text.replace(/[\r\n]+/g, ' ').split(' ');
    let lineLength = 0;
    let ret = [''];
    for (let word of words) {
        if (lineLength + word.length >= maxLineLength) {
            lineLength = word.length;
            ret.push([word]); 
        } else {
            lineLength += word.length+1;
            ret[ret.length-1]+=word+' ';
        }
    }
    return ret;
}

export function camelize(str) {
    return str.replace(/(?:^\w|[A-Z]|\b\w)/g, function(word, index) {
        return word.toUpperCase();
    }).replace(/\s+/g, '');
}

export const rcpText = {
    rcp60:"existing global policies",
    "rcp85":"worst case scenario"
}

export const seasonText = {
    annual:"yearly",
    winter:"winter",
    summer:"summer"
};

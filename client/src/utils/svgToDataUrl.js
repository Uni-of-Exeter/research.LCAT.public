import { Canvg } from 'canvg';

/**
 * Converts an SVG string to a data URL that can be used in PDF reports
 * @param {string} svgString - The SVG content as a string
 * @param {number} width - Desired width of the output image
 * @param {number} height - Desired height of the output image
 * @returns {Promise<string>} - Data URL of the converted image
 */
export const svgToDataUrl = async (svgString, width = 200, height = 60) => {
    try {
        // Create a canvas element
        const canvas = document.createElement('canvas');
        canvas.width = width;
        canvas.height = height;
        
        const ctx = canvas.getContext('2d');
        
        // Create canvg instance
        const v = Canvg.fromString(ctx, svgString);
        
        // Render the SVG to canvas
        await v.render();
        
        // Convert canvas to data URL
        return canvas.toDataURL('image/png');
    } catch (error) {
        console.error('Error converting SVG to data URL:', error);
        throw error;
    }
};

/**
 * Loads an SVG file and converts it to a data URL
 * @param {string} svgPath - Path to the SVG file
 * @param {number} width - Desired width of the output image
 * @param {number} height - Desired height of the output image
 * @returns {Promise<string>} - Data URL of the converted image
 */
export const loadSvgAsDataUrl = async (svgPath, width = 200, height = 60) => {
    try {
        const response = await fetch(svgPath);
        const svgString = await response.text();
        return await svgToDataUrl(svgString, width, height);
    } catch (error) {
        console.error('Error loading SVG file:', error);
        throw error;
    }
};

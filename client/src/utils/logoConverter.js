// Utility function to convert SVG to data URL using canvg
export const convertSvgToDataUrl = async (svgUrl) => {
    try {
        // Load the SVG content
        const response = await fetch(svgUrl);
        const svgString = await response.text();
        
        // Create a canvas element
        const canvas = document.createElement('canvas');
        canvas.width = 200;
        canvas.height = 60;
        
        const ctx = canvas.getContext('2d');
        
        // Create canvg instance and render
        const { Canvg } = await import('canvg');
        const v = Canvg.fromString(ctx, svgString);
        await v.render();
        
        // Convert canvas to data URL
        return canvas.toDataURL('image/png');
    } catch (error) {
        console.error('Failed to convert logo:', error);
        return null;
    }
};

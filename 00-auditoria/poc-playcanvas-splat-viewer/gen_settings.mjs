import { defaultSettings } from '@playcanvas/supersplat-viewer/settings';
import { writeFileSync } from 'fs';
const settings = defaultSettings();
writeFileSync('settings.json', JSON.stringify(settings, null, 2));
console.log('wrote settings.json');

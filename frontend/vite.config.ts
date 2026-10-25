import {defineConfig} from 'vitest/config';
import {fileURLToPath} from 'node:url';
const publicSources=['.','../docs/articles','../docs/media','../docs/evidence'].map(path=>fileURLToPath(new URL(path,import.meta.url)));
export default defineConfig({server:{fs:{allow:publicSources},proxy:{'/api':'http://127.0.0.1:8090'}},test:{environment:'jsdom',setupFiles:['./src/test-setup.ts'],restoreMocks:true}});

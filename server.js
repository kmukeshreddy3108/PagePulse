import express from 'express';
import cors from 'cors';
import path from 'path';
import { fileURLToPath } from 'url';
import * as cheerio from 'cheerio';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
const PORT = process.env.PORT || 3000;

app.use(cors());
app.use(express.json());

function isForbiddenHost(hostname) {
    const host = hostname.toLowerCase().trim();
    if (
        host === 'localhost' ||
        host.endsWith('.localhost') ||
        host === 'localhost.localdomain' ||
        host === '127.0.0.1' ||
        host === '0.0.0.0' ||
        host === '::1' ||
        host === '[::1]'
    ) {
        return true;
    }
    const ipv4Match = host.match(/^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})$/);
    if (ipv4Match) {
        const [, a, b] = ipv4Match.map(Number);
        if (a === 10) return true;
        if (a === 127) return true;
        if (a === 169 && b === 254) return true;
        if (a === 172 && b >= 16 && b <= 31) return true;
        if (a === 192 && b === 168) return true;
        if (a === 0) return true;
    }
    return false;
}

function validateUrl(rawUrl) {
    if (!rawUrl || typeof rawUrl !== 'string' || !rawUrl.trim()) {
        throw { status: 400, message: 'URL must not be empty.' };
    }
    const candidate = rawUrl.trim();
    let parsed;
    try { parsed = new URL(candidate); }
    catch { throw { status: 400, message: 'The provided URL is invalid.' }; }
    if (!['http:', 'https:'].includes(parsed.protocol)) {
        throw { status: 400, message: 'URL must start with http:// or https://.' };
    }
    if (!parsed.hostname) {
        throw { status: 400, message: 'URL is missing a valid domain/host.' };
    }
    const host = parsed.hostname;
    if (isForbiddenHost(host)) {
        throw { status: 400, message: 'Access to private/internal IP addresses or localhost is forbidden.' };
    }
    if (!host.includes('.') && host !== 'localhost') {
        throw { status: 400, message: 'URL does not contain a valid domain.' };
    }
    return candidate;
}

async function handleAudit(req, res) {
    let targetUrl;
    try { targetUrl = validateUrl(req.body?.url); }
    catch (err) { return res.status(err.status || 400).json({ detail: err.message || 'Invalid URL' }); }
    const startTime = performance.now();
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 10000);
    try {
        const response = await fetch(targetUrl, {
            method: 'GET',
            headers: {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
            },
            signal: controller.signal,
            redirect: 'follow',
        });
        clearTimeout(timeoutId);
        const elapsedTime = Number(((performance.now() - startTime) / 1000).toFixed(3));
        const contentType = response.headers.get('content-type') || '';
        const htmlText = await response.text();
        const isHtmlType = contentType.toLowerCase().includes('html') || contentType.toLowerCase().includes('xml');
        const isHtmlBody = htmlText.trim().toLowerCase().startsWith('<!doctype') || htmlText.trim().toLowerCase().includes('<html');
        if (!isHtmlType && !isHtmlBody && contentType) {
            return res.status(415).json({ detail: `Expected an HTML document but received Content-Type '${contentType || 'unknown'}'.` });
        }
        if (Buffer.byteLength(htmlText, 'utf8') > 5 * 1024 * 1024) {
            return res.status(500).json({ detail: 'Target response size exceeds maximum allowed limit (5MB).' });
        }
        const $ = cheerio.load(htmlText);
        const titleRaw = $('title').first().text().trim();
        const page_title = titleRaw || null;
        let metaDesc = $('meta[name="description" i]').attr('content') || $('meta[property="og:description" i]').attr('content');
        metaDesc = metaDesc ? metaDesc.trim() || null : null;
        const h1_count = $('h1').length;
        let images_missing_alt = 0;
        $('img').each((_, el) => {
            const alt = $(el).attr('alt');
            if (alt === undefined || alt === null || !alt.trim()) { images_missing_alt++; }
        });
        $('script, style, noscript, iframe, svg').remove();
        const bodyText = $('body').text().replace(/\s+/g, ' ').trim();
        const word_count = bodyText ? bodyText.split(/\s+/).filter(Boolean).length : 0;
        return res.json({
            status: response.status,
            response_time: elapsedTime,
            page_title,
            meta_description: metaDesc,
            h1_count,
            images_missing_alt,
            word_count,
        });
    } catch (err) {
        clearTimeout(timeoutId);
        if (err.name === 'AbortError') {
            return res.status(408).json({ detail: `Request to ${targetUrl} timed out after 10s.` });
        }
        return res.status(500).json({ detail: `Could not reach ${targetUrl}: ${err.message || 'Upstream fetch error'}` });
    }
}

app.post('/api/v1/audit', handleAudit);
app.post('/api/audit', handleAudit);
app.post('/audit', handleAudit);


if (process.env.NODE_ENV !== 'production') {
    const { createServer: createViteServer } = await import('vite');
    const vite = await createViteServer({ server: { middlewareMode: true }, appType: 'spa' });
    app.use(vite.middlewares);
} else {
    app.use(express.static(path.join(__dirname, 'dist')));
    app.get('*', (req, res) => {
        res.sendFile(path.join(__dirname, 'dist', 'index.html'));
    });
}

app.listen(PORT, '0.0.0.0', () => {
    console.log(`Page Pulse server listening on http://0.0.0.0:${PORT}`);
});

export default {
  async fetch(request, env, ctx) {
    const urls = [
      "https://www.google.com/",
      "https://warranty.vnsamsungcampaign.com/",
      "https://warranty.vnsamsungcampaign.com/api/index.php?imei=423432411111111"
    ];

    const results = await Promise.all(
      urls.map(async (url) => {
        const start = Date.now();

        try {
          const response = await fetch(url, {
            headers: {
              "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
              "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
              "Accept-Language": "vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7",
      
            }
          });

          const body = await response.text();

          return {
            URL: url,
            Status: response.status,
            Time: Date.now() - start + " ms",
            Response: body.slice(0, 300)
          };

        } catch (error) {
          return {
            URL: url,
            Error: error.message,
            Time: Date.now() - start + " ms"
          };
        }
      })
    );

    return Response.json(results);
  }
};

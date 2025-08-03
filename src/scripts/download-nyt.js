(async function() {
    // Generate array of dates from March 2025 to July 2025
    const dates = [];
    const startDate = new Date('2025-01-01');
    const endDate = new Date('2025-07-31');
    
    for (let d = new Date(startDate); d <= endDate; d.setDate(d.getDate() + 1)) {
        const year = d.getFullYear();
        const month = String(d.getMonth() + 1).padStart(2, '0');
        const day = String(d.getDate()).padStart(2, '0');
        dates.push(`${year}-${month}-${day}`);
    }
    
    console.log(`Fetching ${dates.length} puzzles from ${dates[0]} to ${dates[dates.length - 1]}`);
    console.log('NOTE: If running from outside nytimes.com, you may need to visit https://cors-anywhere.herokuapp.com/corsdemo first');
    
    const results = [];
    
    // Function to wait for specified milliseconds
    const wait = (ms) => new Promise(resolve => setTimeout(resolve, ms));
    
    // Function to download JSON
    const downloadJSON = (data, filename) => {
        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    };
    
    // Detect if we're on nytimes.com
    const isOnNYT = window.location.hostname.includes('nytimes.com');
    
    // Loop through each date
    for (let i = 0; i < dates.length; i++) {
        const date = dates[i];
        console.log(`Fetching puzzle ${i + 1}/${dates.length}: ${date}`);
        
        try {
            // Use different URL based on where we're running from
            const baseUrl = isOnNYT 
                ? `https://www.nytimes.com/svc/crosswords/v6/puzzle/mini/${date}.json`
                : `https://api.allorigins.win/get?url=${encodeURIComponent(`https://www.nytimes.com/svc/crosswords/v6/puzzle/mini/${date}.json`)}`;
            
            const fetchOptions = isOnNYT ? {
                "credentials": "include",
                "headers": {
                    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:141.0) Gecko/20100101 Firefox/141.0",
                    "Accept": "application/json,*/*",
                    "Accept-Language": "en-US,en;q=0.5",
                    "X-Games-Auth-Bypass": "true",
                    "Pragma": "no-cache",
                    "Cache-Control": "no-cache"
                },
                "method": "GET"
            } : {
                "method": "GET"
            };
            
            const response = await fetch(baseUrl, fetchOptions);
            
            if (response.ok) {
                let data;
                if (isOnNYT) {
                    data = await response.json();
                } else {
                    const proxyResponse = await response.json();
                    data = JSON.parse(proxyResponse.contents);
                }
                
                results.push({
                    date: date,
                    success: true,
                    data: data
                });
                console.log(`✓ Successfully fetched ${date}`);
            } else {
                console.log(`✗ Failed to fetch ${date}: ${response.status} ${response.statusText}`);
                results.push({
                    date: date,
                    success: false,
                    error: `${response.status} ${response.statusText}`
                });
            }
        } catch (error) {
            console.log(`✗ Error fetching ${date}:`, error.message);
            results.push({
                date: date,
                success: false,
                error: error.message
            });
        }
        
        // Wait 1 second before next request (except for the last one)
        if (i < dates.length - 1) {
            await wait(1000);
        }
    }
    
    console.log(`Completed! Successfully fetched ${results.filter(r => r.success).length}/${results.length} puzzles`);
    
    // Download results as JSON
    const filename = `nyt_crosswords_jan_jul_2025_${new Date().toISOString().split('T')[0]}.json`;
    downloadJSON(results, filename);
    
    console.log(`Results downloaded as ${filename}`);
    
    return results;
})();
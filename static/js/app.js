document.addEventListener("DOMContentLoaded", () => {
    // ----------------------------------------------------------------
    // 1. Navigation and View Switching Logic
    // ----------------------------------------------------------------
    const navItems = document.querySelectorAll(".nav-item");
    const viewPanes = document.querySelectorAll(".view-pane");

    // Global variable to track active ECharts instances for resizing
    let activeCharts = [];

    navItems.forEach(item => {
        item.addEventListener("click", () => {
            const targetView = item.getAttribute("data-view");

            // Update navigation item active state
            navItems.forEach(n => n.classList.remove("active"));
            item.classList.add("active");

            // Toggle active view panel
            viewPanes.forEach(pane => {
                pane.classList.remove("active");
                if (pane.id === targetView) {
                    pane.classList.add("active");
                }
            });

            // Trigger ECharts resize to fit newly visible container grids
            setTimeout(() => {
                activeCharts.forEach(chart => chart.resize());
            }, 100);
        });
    });

    // ----------------------------------------------------------------
    // 2. Predictive Slider Sync Label Logic
    // ----------------------------------------------------------------
    const sliders = [
        { id: "housing_median_age", bubbleId: "val-age", format: v => `${v} Years` },
        { id: "median_income", bubbleId: "val-income", format: v => `$${(parseFloat(v) * 10000).toLocaleString(undefined, { maximumFractionDigits: 0 })}` },
        { id: "total_rooms", bubbleId: "val-rooms", format: v => parseInt(v).toLocaleString() },
        { id: "total_bedrooms", bubbleId: "val-bedrooms", format: v => parseInt(v).toLocaleString() },
        { id: "population", bubbleId: "val-population", format: v => parseInt(v).toLocaleString() },
        { id: "households", bubbleId: "val-households", format: v => parseInt(v).toLocaleString() }
    ];

    sliders.forEach(sliderDef => {
        const sliderEl = document.getElementById(sliderDef.id);
        const bubbleEl = document.getElementById(sliderDef.bubbleId);

        if (sliderEl && bubbleEl) {
            const updateBubble = () => {
                bubbleEl.textContent = sliderDef.format(sliderEl.value);
            };

            // Bind inputs for realtime synchronization
            sliderEl.addEventListener("input", updateBubble);
            updateBubble(); // Init value
        }
    });

    // Latitude & Longitude direct inputs text bubble sync
    const latInput = document.getElementById("latitude");
    const lngInput = document.getElementById("longitude");
    const latBubble = document.getElementById("val-latitude");
    const lngBubble = document.getElementById("val-longitude");

    const syncCoordBubbles = () => {
        if (latInput && latBubble) latBubble.textContent = parseFloat(latInput.value).toFixed(4);
        if (lngInput && lngBubble) lngBubble.textContent = parseFloat(lngInput.value).toFixed(4);
    };

    if (latInput && lngInput) {
        latInput.addEventListener("input", syncCoordBubbles);
        lngInput.addEventListener("input", syncCoordBubbles);
        syncCoordBubbles();
    }

    // ----------------------------------------------------------------
    // 3. Overview Dashboard Statistics Fetching & ECharts Setup
    // ----------------------------------------------------------------
    const fetchDashboardAnalytics = async () => {
        try {
            const response = await fetch("/api/statistics");
            if (!response.ok) throw new Error("Failed to fetch analytics statistics");
            const data = await response.json();

            // Populate KPI metrics
            document.getElementById("kpi-total-records").textContent = data.kpis.total_records.toLocaleString();
            document.getElementById("kpi-avg-price").textContent = `$${Math.round(data.kpis.avg_house_value).toLocaleString()}`;
            document.getElementById("kpi-avg-income").textContent = `$${Math.round(data.kpis.avg_income).toLocaleString()}`;
            document.getElementById("kpi-avg-age").textContent = `${Math.round(data.kpis.avg_age)} Yrs`;

            // Initialize ECharts instances
            initPriceDistributionChart(data.price_distribution);
            initOceanProximityChart(data.ocean_proximity_stats);
            initIncomeScatterChart(data.scatter_data);
            initCorrelationHeatmap(data.correlation);

        } catch (error) {
            console.error("Dashboard Analytics Error:", error);
        }
    };

    const initPriceDistributionChart = (distData) => {
        const chartDom = document.getElementById("chart-price-distribution");
        if (!chartDom) return;
        const myChart = echarts.init(chartDom);
        activeCharts.push(myChart);

        const xData = distData.bins.slice(0, -1).map((b, idx) => {
            const nextB = distData.bins[idx + 1];
            return `$${Math.round(b / 1000)}k-$${Math.round(nextB / 1000)}k`;
        });

        const option = {
            tooltip: { trigger: "axis", axisPointer: { type: "shadow" } },
            grid: { top: "10%", left: "3%", right: "3%", bottom: "10%", containLabel: true },
            xAxis: { type: "category", data: xData, axisLabel: { interval: 1, rotate: 30, color: "#9ca3af" } },
            yAxis: { type: "value", splitLine: { lineStyle: { color: "rgba(255,255,255,0.05)" } }, axisLabel: { color: "#9ca3af" } },
            series: [{
                name: "Record Count",
                type: "bar",
                data: distData.counts,
                itemStyle: {
                    color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                        { offset: 0, color: "#818cf8" },
                        { offset: 1, color: "#4f46e5" }
                    ]),
                    borderRadius: [4, 4, 0, 0]
                }
            }]
        };

        myChart.setOption(option);
    };

    const initOceanProximityChart = (oceanData) => {
        const chartDom = document.getElementById("chart-ocean-proximity");
        if (!chartDom) return;
        const myChart = echarts.init(chartDom);
        activeCharts.push(myChart);

        const option = {
            tooltip: { trigger: "axis" },
            legend: { data: ["Avg House Value", "Avg Household Income"], textStyle: { color: "#9ca3af" }, top: "0%" },
            grid: { top: "15%", left: "3%", right: "3%", bottom: "5%", containLabel: true },
            xAxis: { type: "category", data: oceanData.categories, axisLabel: { color: "#9ca3af" } },
            yAxis: [
                {
                    type: "value",
                    name: "House Value",
                    position: "left",
                    axisLabel: { formatter: "${value}", color: "#9ca3af" },
                    splitLine: { lineStyle: { color: "rgba(255,255,255,0.05)" } }
                },
                {
                    type: "value",
                    name: "Income",
                    position: "right",
                    axisLabel: { formatter: "${value}", color: "#9ca3af" },
                    splitLine: { show: false }
                }
            ],
            series: [
                {
                    name: "Avg House Value",
                    type: "bar",
                    data: oceanData.avg_prices,
                    itemStyle: {
                        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                            { offset: 0, color: "#c084fc" },
                            { offset: 1, color: "#9333ea" }
                        ]),
                        borderRadius: [4, 4, 0, 0]
                    }
                },
                {
                    name: "Avg Household Income",
                    type: "line",
                    yAxisIndex: 1,
                    data: oceanData.avg_incomes,
                    symbolSize: 8,
                    lineStyle: { width: 3, color: "#10b981" },
                    itemStyle: { color: "#10b981" }
                }
            ]
        };

        myChart.setOption(option);
    };

    const initIncomeScatterChart = (scatterData) => {
        const chartDom = document.getElementById("chart-income-scatter");
        if (!chartDom) return;
        const myChart = echarts.init(chartDom);
        activeCharts.push(myChart);

        const option = {
            tooltip: {
                trigger: "item",
                formatter: (params) => {
                    const val = params.value;
                    return `
                        <div style="font-family: Inter; padding: 4px;">
                            <b style="color: #818cf8;">Neighborhood Node</b><br/>
                            Income: <b>$${(val[0]*10000).toLocaleString(undefined, {maximumFractionDigits: 0})}</b><br/>
                            House Price: <b>$${val[1].toLocaleString()}</b><br/>
                            Median Age: <b>${val[2]} Years</b>
                        </div>
                    `;
                }
            },
            grid: { top: "10%", left: "3%", right: "15%", bottom: "5%", containLabel: true },
            xAxis: {
                type: "value",
                name: "Median Income ($x10k)",
                nameTextStyle: { color: "#9ca3af" },
                splitLine: { lineStyle: { color: "rgba(255,255,255,0.05)" } },
                axisLabel: { color: "#9ca3af" }
            },
            yAxis: {
                type: "value",
                name: "House Value ($)",
                nameTextStyle: { color: "#9ca3af" },
                splitLine: { lineStyle: { color: "rgba(255,255,255,0.05)" } },
                axisLabel: { color: "#9ca3af" }
            },
            visualMap: {
                min: 1,
                max: 52,
                dimension: 2,
                orient: "vertical",
                right: 10,
                top: "center",
                text: ["Old Age", "New Build"],
                calculable: true,
                inRange: {
                    color: ["#10b981", "#eab308", "#f97316", "#ef4444"]
                },
                textStyle: { color: "#9ca3af" }
            },
            series: [{
                name: "Neighborhoods",
                type: "scatter",
                data: scatterData,
                symbolSize: 6,
                itemStyle: { opacity: 0.75 }
            }]
        };

        myChart.setOption(option);
    };

    const initCorrelationHeatmap = (corrData) => {
        const chartDom = document.getElementById("chart-correlation-heatmap");
        if (!chartDom) return;
        const myChart = echarts.init(chartDom);
        activeCharts.push(myChart);

        const columns = corrData.columns.map(c => c.replace(/_/g, " "));
        const data = [];
        for (let i = 0; i < corrData.values.length; i++) {
            for (let j = 0; j < corrData.values[i].length; j++) {
                data.push([j, i, corrData.values[i][j]]);
            }
        }

        const option = {
            tooltip: {
                position: "top",
                formatter: (params) => {
                    return `${columns[params.value[0]]} vs ${columns[params.value[1]]}: <b>${params.value[2]}</b>`;
                }
            },
            grid: { top: "5%", left: "3%", right: "5%", bottom: "15%", containLabel: true },
            xAxis: {
                type: "category",
                data: columns,
                axisLabel: { interval: 0, rotate: 30, color: "#9ca3af" },
                splitArea: { show: true }
            },
            yAxis: {
                type: "category",
                data: columns,
                axisLabel: { color: "#9ca3af" },
                splitArea: { show: true }
            },
            visualMap: {
                min: -1,
                max: 1,
                calculable: true,
                orient: "horizontal",
                left: "center",
                bottom: "0%",
                inRange: {
                    color: ["#ef4444", "#ffffff", "#6366f1"]
                },
                textStyle: { color: "#9ca3af" }
            },
            series: [{
                name: "Correlation Coefficient",
                type: "heatmap",
                data: data,
                label: {
                    show: true,
                    formatter: (params) => params.value[2],
                    color: "#000000",
                    fontWeight: 600
                },
                emphasis: {
                    itemStyle: {
                        shadowBlur: 10,
                        shadowColor: "rgba(0, 0, 0, 0.5)"
                    }
                }
            }]
        };

        myChart.setOption(option);
    };

    // Make charts fully responsive
    window.addEventListener("resize", () => {
        activeCharts.forEach(chart => chart.resize());
    });

    // ----------------------------------------------------------------
    // 4. Spatial Coordinate Scatter Chart (ECharts)
    // ----------------------------------------------------------------
    const initializeGeographicScatterChart = async () => {
        try {
            const response = await fetch("/api/map-data");
            if (!response.ok) throw new Error("Failed to load coordinate datasets");
            const coordsData = await response.json();

            const chartDom = document.getElementById("chart-geo-scatter");
            if (!chartDom) return;
            const myChart = echarts.init(chartDom);
            activeCharts.push(myChart);

            // Format coordinates data as coordinates scatter points [longitude, latitude, price, income, age, proximity]
            const formattedData = coordsData.map(point => [
                point.longitude,
                point.latitude,
                point.median_house_value,
                point.median_income * 10000,
                point.housing_median_age,
                point.ocean_proximity
            ]);

            const option = {
                tooltip: {
                    trigger: "item",
                    formatter: (params) => {
                        const val = params.value;
                        return `
                            <div style="font-family: Inter; padding: 6px; line-height: 1.5; color: #f3f4f6;">
                                <b style="color: #a855f7; font-size: 0.95rem; font-family: Outfit;">Census Neighborhood Node</b><br/>
                                Coordinates: <b>${val[1].toFixed(4)}&deg; N, ${val[0].toFixed(4)}&deg; W</b><br/>
                                Median Price: <b style="color: #818cf8; font-family: Outfit; font-size: 1rem;">$${val[2].toLocaleString()}</b><br/>
                                Median Income: <b>$${val[3].toLocaleString(undefined, { maximumFractionDigits: 0 })}</b><br/>
                                Housing Age: <b>${val[4]} Years</b><br/>
                                Proximity: <b>${val[5]}</b>
                            </div>
                        `;
                    }
                },
                grid: { top: "5%", left: "5%", right: "18%", bottom: "8%", containLabel: true },
                xAxis: {
                    type: "value",
                    name: "Longitude (Degrees West)",
                    nameLocation: "middle",
                    nameGap: 30,
                    nameTextStyle: { color: "#9ca3af", fontWeight: 600, fontSize: 12 },
                    splitLine: { lineStyle: { color: "rgba(255,255,255,0.05)" } },
                    axisLabel: { color: "#9ca3af" },
                    scale: true
                },
                yAxis: {
                    type: "value",
                    name: "Latitude (Degrees North)",
                    nameLocation: "middle",
                    nameGap: 40,
                    nameTextStyle: { color: "#9ca3af", fontWeight: 600, fontSize: 12 },
                    splitLine: { lineStyle: { color: "rgba(255,255,255,0.05)" } },
                    axisLabel: { color: "#9ca3af" },
                    scale: true
                },
                visualMap: {
                    min: 15000,
                    max: 500001,
                    dimension: 2,
                    orient: "vertical",
                    right: 15,
                    top: "center",
                    text: ["$500k+", "$15k"],
                    calculable: true,
                    inRange: {
                        color: ["#6366f1", "#10b981", "#eab308", "#f97316", "#ef4444"]
                    },
                    textStyle: { color: "#9ca3af" }
                },
                series: [{
                    name: "Census Tracts",
                    type: "scatter",
                    data: formattedData,
                    symbolSize: 6,
                    itemStyle: {
                        opacity: 0.85,
                        shadowBlur: 2,
                        shadowColor: "rgba(0,0,0,0.5)"
                    }
                }],
                // Enable zoom & pan interactively (drag to pan, mousewheel to zoom)
                dataZoom: [
                    {
                        type: "inside",
                        disabled: false
                    }
                ]
            };

            myChart.setOption(option);

        } catch (error) {
            console.error("Geographic Scatter Chart error:", error);
        }
    };

    // ----------------------------------------------------------------
    // 5. Predictor Submission Pipeline integration
    // ----------------------------------------------------------------
    const predictionForm = document.getElementById("prediction-form");
    const predPlaceholder = document.getElementById("prediction-placeholder");
    const predLoader = document.getElementById("prediction-loader");
    const predResult = document.getElementById("prediction-result");

    const priceDisplay = document.getElementById("predicted-price-display");
    const resCoord = document.getElementById("res-coord");
    const resIncome = document.getElementById("res-income");
    const resAge = document.getElementById("res-age");
    const resRooms = document.getElementById("res-rooms");

    if (predictionForm) {
        predictionForm.addEventListener("submit", async (e) => {
            e.preventDefault();

            // Transition UI displays to loading state
            predPlaceholder.style.display = "none";
            predResult.style.display = "none";
            predLoader.style.display = "flex";

            // Compile input payload
            const payload = {
                longitude: parseFloat(lngInput.value),
                latitude: parseFloat(latInput.value),
                housing_median_age: parseFloat(document.getElementById("housing_median_age").value),
                total_rooms: parseFloat(document.getElementById("total_rooms").value),
                total_bedrooms: parseFloat(document.getElementById("total_bedrooms").value),
                population: parseFloat(document.getElementById("population").value),
                households: parseFloat(document.getElementById("households").value),
                median_income: parseFloat(document.getElementById("median_income").value),
                ocean_proximity: document.getElementById("ocean_proximity").value
            };

            try {
                // Post asynchronous payload to pipeline prediction endpoint
                const response = await fetch("/api/predict", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(payload)
                });

                if (!response.ok) {
                    const errRes = await response.json();
                    throw new Error(errRes.error || "Execution failed on the model prediction pipeline");
                }

                const result = await response.json();

                // Mock premium analytics processing delay for visual feel (600ms)
                setTimeout(() => {
                    predLoader.style.display = "none";
                    predResult.style.display = "block";

                    // Update predicted metrics displays
                    priceDisplay.textContent = result.formatted_price;

                    // Scale price glowing effect depending on valuation bracket
                    if (result.predicted_price >= 350000) {
                        priceDisplay.style.backgroundImage = "linear-gradient(135deg, #ef4444 0%, #f97316 100%)";
                    } else if (result.predicted_price >= 200000) {
                        priceDisplay.style.backgroundImage = "var(--primary-gradient)";
                    } else {
                        priceDisplay.style.backgroundImage = "linear-gradient(135deg, #6366f1 0%, #10b981 100%)";
                    }

                    // Populate informational card highlights
                    resCoord.textContent = `${payload.latitude.toFixed(2)}, ${payload.longitude.toFixed(2)}`;
                    resIncome.textContent = `$${(payload.median_income * 10000).toLocaleString(undefined, { maximumFractionDigits: 0 })}`;
                    resAge.textContent = `${payload.housing_median_age} Yrs`;
                    resRooms.textContent = `${payload.total_rooms.toLocaleString()} / ${payload.total_bedrooms.toLocaleString()}`;

                }, 600);

            } catch (err) {
                predLoader.style.display = "none";
                predPlaceholder.style.display = "block";
                alert(`Error: ${err.message}`);
            }
        });
    }

    // Reset Predictor View back to start state
    const resetBtn = document.getElementById("reset-prediction-btn");
    if (resetBtn) {
        resetBtn.addEventListener("click", () => {
            predResult.style.display = "none";
            predPlaceholder.style.display = "block";
        });
    }

    // ----------------------------------------------------------------
    // 6. Page Core Initializer
    // ----------------------------------------------------------------
    const runInitialization = async () => {
        // Fetch background server analytics and populate charts
        await fetchDashboardAnalytics();
        
        // Initialize geographic coordinate scatter chart
        await initializeGeographicScatterChart();
    };

    runInitialization();
});

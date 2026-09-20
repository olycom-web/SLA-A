# -*- coding: utf-8 -*-
"""
A-Share Continuous Dividend Analysis & HTML Dashboard Generator
Criteria:
  1. Never interrupted cash dividends since IPO
  2. Market Cap >= 200 亿元 only
  3. Exclude Beijing Stock Exchange (北交所) & STAR Market (科创板 688)
"""
import json
import csv
import statistics
from generate_dividend_analysis import DATA

stocks = DATA

# Sort by market cap descending
stocks.sort(key=lambda x: x["market_cap"], reverse=True)

# 1. Output JSON
with open("dividend_continuous_stocks.json", "w", encoding="utf-8") as f:
    json.dump(stocks, f, ensure_ascii=False, indent=2)
print("Saved dividend_continuous_stocks.json")

# 2. Output CSV
fieldnames = [
    "code", "name", "industry", "listing_date", "continuous_div_years",
    "market_cap", "float_cap", "dividend_yield", "cagr_5y_non_drip", "cagr_5y_drip",
    "is_less_than_5y", "actual_years_calculated", "business_scope",
    "overseas_rev_pct", "domestic_rev_pct", "geography_detail", "business_model_moat", "div_policy"
]
with open("dividend_continuous_stocks.csv", "w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    for row in stocks:
        writer.writerow(row)
print("Saved dividend_continuous_stocks.csv")

# Metrics
total_stocks = len(stocks)
total_cap = sum(s["market_cap"] for s in stocks)
avg_cap = total_cap / total_stocks
median_cap = statistics.median(s["market_cap"] for s in stocks)
max_cap = max(s["market_cap"] for s in stocks)
min_cap = min(s["market_cap"] for s in stocks)
avg_yield = sum(s["dividend_yield"] for s in stocks) / total_stocks
avg_drip = sum(s["cagr_5y_drip"] for s in stocks) / total_stocks
avg_non_drip = sum(s["cagr_5y_non_drip"] for s in stocks) / total_stocks
drip_spread = avg_drip - avg_non_drip

# Geographic breakdowns
global_list = [s for s in stocks if s["business_scope"] == "全球生意"]
china_list = [s for s in stocks if s["business_scope"] == "全国大部分在中国"]
region_list = [s for s in stocks if s["business_scope"] == "特定区域生意"]

global_count = len(global_list)
china_count = len(china_list)
region_count = len(region_list)

global_cap = sum(s["market_cap"] for s in global_list)
china_cap = sum(s["market_cap"] for s in china_list)
region_cap = sum(s["market_cap"] for s in region_list)

global_avg_overseas = sum(s["overseas_rev_pct"] for s in global_list) / global_count
china_avg_overseas = sum(s["overseas_rev_pct"] for s in china_list) / china_count
region_avg_overseas = sum(s["overseas_rev_pct"] for s in region_list) / region_count

global_avg_yield = sum(s["dividend_yield"] for s in global_list) / global_count
china_avg_yield = sum(s["dividend_yield"] for s in china_list) / china_count
region_avg_yield = sum(s["dividend_yield"] for s in region_list) / region_count

global_avg_drip = sum(s["cagr_5y_drip"] for s in global_list) / global_count
china_avg_drip = sum(s["cagr_5y_drip"] for s in china_list) / china_count
region_avg_drip = sum(s["cagr_5y_drip"] for s in region_list) / region_count

global_avg_nondrip = sum(s["cagr_5y_non_drip"] for s in global_list) / global_count
china_avg_nondrip = sum(s["cagr_5y_non_drip"] for s in china_list) / china_count
region_avg_nondrip = sum(s["cagr_5y_non_drip"] for s in region_list) / region_count

# Sub-5 years list
sub5y_list = [s for s in stocks if s["is_less_than_5y"]]

# Cap tiers (>= 200亿)
tier_mega = [s for s in stocks if s["market_cap"] >= 10000]
tier_large = [s for s in stocks if 3000 <= s["market_cap"] < 10000]
tier_mid = [s for s in stocks if 1000 <= s["market_cap"] < 3000]
tier_growth = [s for s in stocks if 200 <= s["market_cap"] < 1000]

# Continuous years tiers
years_25plus = [s for s in stocks if s["continuous_div_years"] >= 25]
years_15to24 = [s for s in stocks if 15 <= s["continuous_div_years"] < 25]
years_5to14 = [s for s in stocks if 5 <= s["continuous_div_years"] < 15]
years_under5 = [s for s in stocks if s["continuous_div_years"] < 5]

# Top DRIP
top_drip = sorted(stocks, key=lambda x: x["cagr_5y_drip"], reverse=True)[:10]

parts = []
parts.append(f"""<!DOCTYPE html>
<html lang="zh-CN" class="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>A股持续分红全勤股深度量化研报 (市值≥200亿 · 排除北交所/688)</title>
    <!-- Tailwind CSS CDN -->
    <script src="https://cdn.tailwindcss.com"></script>
    <script>
        tailwind.config = {{
            darkMode: 'class',
            theme: {{
                extend: {{
                    colors: {{
                        slate: {{
                            850: '#151e2e',
                            950: '#070d18'
                        }}
                    }}
                }}
            }}
        }}
    </script>
    <style>
        .sort-icon::after {{
            content: ' ⇅';
            opacity: 0.35;
            font-size: 0.85em;
        }}
        .sort-asc::after {{
            content: ' ▲';
            opacity: 1;
            color: #38bdf8;
        }}
        .sort-desc::after {{
            content: ' ▼';
            opacity: 1;
            color: #38bdf8;
        }}
        @media print {{
            header, button, select, input, #filter-panel {{
                display: none !important;
            }}
            body {{
                background-color: white !important;
                color: black !important;
            }}
        }}
    </style>
</head>
<body class="bg-slate-950 text-slate-100 min-h-screen transition-colors duration-200 antialiased font-sans">

    <!-- Top Navigation -->
    <header class="border-b border-slate-800 bg-slate-900/90 backdrop-blur sticky top-0 z-50">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
            <div class="flex items-center space-x-3">
                <div class="w-9 h-9 rounded-xl bg-gradient-to-tr from-sky-500 to-indigo-600 flex items-center justify-center font-extrabold text-white text-base shadow-lg shadow-sky-500/25">
                    红
                </div>
                <div>
                    <h1 class="text-base sm:text-lg font-bold tracking-tight text-white flex items-center gap-2">
                        A股持续分红全勤研报 (≥200亿级)
                        <span class="hidden sm:inline-block text-[11px] font-semibold px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">无北交所 · 无688</span>
                    </h1>
                </div>
            </div>
            <div class="flex items-center space-x-3 sm:space-x-5 text-xs sm:text-sm">
                <a href="#geography-analysis" class="text-slate-400 hover:text-sky-400 transition hidden md:inline">全球 vs 国内业务</a>
                <a href="#marketcap-stats" class="text-slate-400 hover:text-sky-400 transition hidden sm:inline">市值统计</a>
                <a href="#drip-analysis" class="text-slate-400 hover:text-sky-400 transition hidden md:inline">5年DRIP复合年化</a>
                <a href="#sub5y-stocks" class="text-slate-400 hover:text-sky-400 transition hidden lg:inline">次新全勤专项</a>
                <a href="#data-table-section" class="text-sky-400 font-semibold hover:text-sky-300 transition">全景数据库</a>
                <button onclick="toggleTheme()" id="themeToggleBtn" class="p-2 rounded-lg bg-slate-800 text-slate-300 hover:text-white border border-slate-700 transition" title="切换明暗模式">
                    🌓
                </button>
            </div>
        </div>
    </header>

    <!-- Main Container -->
    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-10">

        <!-- Executive Hero Alert Banner -->
        <div class="bg-gradient-to-r from-sky-950/80 via-slate-900 to-indigo-950/80 border border-sky-800/40 rounded-2xl p-6 sm:p-8 shadow-2xl relative overflow-hidden">
            <div class="absolute -right-10 -bottom-10 w-96 h-96 bg-sky-500/10 rounded-full blur-3xl pointer-events-none"></div>
            <div class="relative z-10 space-y-4">
                <div class="flex flex-wrap items-center gap-2">
                    <span class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                        <span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
                        条件 1：自IPO上市以来现金分红全勤 · 绝不中断
                    </span>
                    <span class="inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold bg-sky-500/10 text-sky-400 border border-sky-500/20">
                        条件 2：总市值 ≥ 200 亿元
                    </span>
                    <span class="inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold bg-amber-500/10 text-amber-400 border border-amber-500/20">
                        条件 3：排除北交所 · 排除科创板 688
                    </span>
                </div>
                <h2 class="text-2xl sm:text-3xl lg:text-4xl font-extrabold text-white tracking-tight">
                    A股持续分红核心资产深度量化研报 (200亿+市值全勤标的)
                </h2>
                <p class="text-sm sm:text-base text-slate-300 max-w-4xl leading-relaxed">
                    在全市场5300+只A股中，遵照<strong>“上市以来年年分红无中断”、“总市值在200亿元及以上”、“剔除北交所及科创板688代码”</strong>的三重严苛筛选，最终提炼出 <strong>{total_stocks} 只</strong> 经受住宏观与行业周期检验的坚韧资产。涵盖其<strong>总市值 27.55 万亿元的层级结构</strong>、<strong>近5年复合年化（DRIP分红再投资 vs 不drip）</strong>、<strong>上市不足5年次新样本严格按实际持有期年化测算</strong>，并<strong>单独列项深度解构“全球生意 vs 全国/大部分业务在中国 vs 特定区域垄断”</strong>。
                </p>
                <div class="flex flex-wrap items-center gap-3 pt-2">
                    <button onclick="exportCSV()" class="px-4 py-2 text-xs font-semibold bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 rounded-lg shadow transition flex items-center gap-1.5">
                        📥 导出 200亿+ 全勤样本 CSV
                    </button>
                    <button onclick="exportJSON()" class="px-4 py-2 text-xs font-semibold bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 rounded-lg shadow transition flex items-center gap-1.5">
                        📋 复制结构化 JSON
                    </button>
                    <button onclick="window.print()" class="px-4 py-2 text-xs font-semibold bg-sky-600 hover:bg-sky-500 text-white rounded-lg shadow transition flex items-center gap-1.5">
                        🖨️ 打印研报视图
                    </button>
                </div>
            </div>
        </div>

        <!-- KPI Executive Summary Cards -->
        <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
            <div class="bg-slate-900 border border-slate-800 rounded-xl p-4 shadow-sm hover:border-slate-700 transition">
                <div class="text-xs font-medium text-slate-400">持续分红全勤股 (≥200亿)</div>
                <div class="text-2xl font-bold text-white mt-1 flex items-baseline gap-1">
                    {total_stocks} <span class="text-xs font-normal text-slate-400">只</span>
                </div>
                <div class="text-[11px] text-emerald-400 mt-1 font-semibold">
                    主板/创业板 核心蓝筹
                </div>
            </div>

            <div class="bg-slate-900 border border-slate-800 rounded-xl p-4 shadow-sm hover:border-slate-700 transition">
                <div class="text-xs font-medium text-slate-400">总市值规模合计</div>
                <div class="text-2xl font-bold text-white mt-1 flex items-baseline gap-1">
                    {total_cap/10000:.2f} <span class="text-xs font-normal text-slate-400">万亿元</span>
                </div>
                <div class="text-[11px] text-sky-400 mt-1 font-mono">
                    27.55 万亿大盘中枢
                </div>
            </div>

            <div class="bg-slate-900 border border-slate-800 rounded-xl p-4 shadow-sm hover:border-slate-700 transition">
                <div class="text-xs font-medium text-slate-400">市值中位数 / 均值</div>
                <div class="text-2xl font-bold text-white mt-1 flex items-baseline gap-1">
                    {median_cap:,.0f} <span class="text-xs font-normal text-slate-400">亿</span>
                </div>
                <div class="text-[11px] text-slate-400 mt-1">
                    均值: {avg_cap:,.0f} 亿元
                </div>
            </div>

            <div class="bg-slate-900 border border-slate-800 rounded-xl p-4 shadow-sm hover:border-slate-700 transition">
                <div class="text-xs font-medium text-slate-400">最新平均股息率(TTM)</div>
                <div class="text-2xl font-bold text-amber-400 mt-1 flex items-baseline gap-1">
                    {avg_yield:.2f}%
                </div>
                <div class="text-[11px] text-emerald-400 mt-1 font-semibold">
                    超10Y国债 ~275 BP
                </div>
            </div>

            <div class="bg-slate-900 border border-slate-800 rounded-xl p-4 shadow-sm hover:border-slate-700 transition">
                <div class="text-xs font-medium text-slate-400">5年 DRIP 复合年化</div>
                <div class="text-2xl font-bold text-emerald-400 mt-1 flex items-baseline gap-1">
                    +{avg_drip:.2f}%
                </div>
                <div class="text-[11px] text-slate-400 mt-1">
                    分红再投资全收益
                </div>
            </div>

            <div class="bg-slate-900 border border-slate-800 rounded-xl p-4 shadow-sm hover:border-slate-700 transition">
                <div class="text-xs font-medium text-slate-400">DRIP 超额复利剪刀差</div>
                <div class="text-2xl font-bold text-indigo-400 mt-1 flex items-baseline gap-1">
                    +{drip_spread:.2f}% <span class="text-xs font-normal text-slate-400">/年</span>
                </div>
                <div class="text-[11px] text-emerald-400 mt-1">
                    非DRIP年化: {avg_non_drip:.2f}%
                </div>
            </div>
        </div>
""")

# Section 1: Geographic Analysis
parts.append(f"""
        <!-- Section 1: 业务地域范围专项深度剖析 -->
        <section id="geography-analysis" class="space-y-6 pt-4">
            <div class="flex flex-wrap items-center justify-between border-b border-slate-800 pb-3 gap-2">
                <div>
                    <h3 class="text-xl font-bold text-white flex items-center gap-2">
                        <span class="text-sky-400">▌ 专题项 1</span> 业务地域范围专项深度剖析：全球生意 vs 全国大部分在中国 vs 特定区域生意
                    </h3>
                    <p class="text-xs sm:text-sm text-slate-400 mt-1">
                        单独列项剖析：剖析海外营收占比、跨国制造壁垒、内循环基础设施特许权与区域地理垄断性。
                    </p>
                </div>
                <span class="text-xs px-3 py-1 rounded bg-slate-800 text-slate-300 border border-slate-700 font-mono">
                    3大核心阵营横向对标
                </span>
            </div>

            <!-- Comparison Table -->
            <div class="overflow-x-auto rounded-xl border border-slate-800 bg-slate-900/60 shadow-lg">
                <table class="w-full text-left text-xs sm:text-sm text-slate-300">
                    <thead class="bg-slate-800 text-slate-200 text-xs font-semibold uppercase tracking-wider">
                        <tr>
                            <th class="p-3.5 whitespace-nowrap">业务地域分类</th>
                            <th class="p-3.5 whitespace-nowrap text-center">样本家数及占比</th>
                            <th class="p-3.5 whitespace-nowrap text-right">总市值(亿元)</th>
                            <th class="p-3.5 whitespace-nowrap text-right">平均海外营收占比</th>
                            <th class="p-3.5 whitespace-nowrap text-right">最新平均股息率</th>
                            <th class="p-3.5 whitespace-nowrap text-right text-emerald-400 font-bold">5年DRIP复合年化</th>
                            <th class="p-3.5 whitespace-nowrap text-right">5年非DRIP复合年化</th>
                            <th class="p-3.5 whitespace-nowrap text-right text-indigo-300">DRIP年化增益</th>
                            <th class="p-3.5 min-w-[240px]">代表龙头标的 (市值≥200亿)</th>
                        </tr>
                    </thead>
                    <tbody class="divide-y divide-slate-800">
                        <tr class="hover:bg-slate-800/40 transition">
                            <td class="p-3.5 font-bold text-sky-400 flex items-center gap-2 whitespace-nowrap">
                                <span class="w-2.5 h-2.5 rounded-full bg-sky-400"></span> 全球生意 (Global)
                            </td>
                            <td class="p-3.5 text-center font-semibold text-white">{global_count} 家 ({global_count/total_stocks*100:.1f}%)</td>
                            <td class="p-3.5 text-right font-mono">{global_cap:,.0f}</td>
                            <td class="p-3.5 text-right font-mono font-bold text-sky-300">{global_avg_overseas:.1f}%</td>
                            <td class="p-3.5 text-right font-mono text-amber-300">{global_avg_yield:.2f}%</td>
                            <td class="p-3.5 text-right font-mono font-bold text-emerald-400 text-sm">+{global_avg_drip:.2f}%</td>
                            <td class="p-3.5 text-right font-mono text-slate-300">+{global_avg_nondrip:.2f}%</td>
                            <td class="p-3.5 text-right font-mono text-indigo-300 font-semibold">+{global_avg_drip-global_avg_nondrip:.2f}%/年</td>
                            <td class="p-3.5 text-slate-300 leading-relaxed text-xs">
                                华利集团 (96.8%)、药明康德 (78.2%)、工业富联 (76.5%)、玲珑轮胎 (49.5%)、福耀玻璃 (46.5%)、紫金矿业 (42.5%)、美的集团 (41.5%)、迈瑞医疗 (41.2%)、江铃汽车 (38.5%)、三七互娱 (36.5%)、海康威视 (35.8%)、宁德时代 (34.5%)
                            </td>
                        </tr>
                        <tr class="hover:bg-slate-800/40 transition">
                            <td class="p-3.5 font-bold text-emerald-400 flex items-center gap-2 whitespace-nowrap">
                                <span class="w-2.5 h-2.5 rounded-full bg-emerald-400"></span> 全国大部分业务在中国 (Domestic)
                            </td>
                            <td class="p-3.5 text-center font-semibold text-white">{china_count} 家 ({china_count/total_stocks*100:.1f}%)</td>
                            <td class="p-3.5 text-right font-mono font-bold text-white">{china_cap:,.0f}</td>
                            <td class="p-3.5 text-right font-mono text-slate-400">{china_avg_overseas:.1f}% (国内 {100-china_avg_overseas:.1f}%)</td>
                            <td class="p-3.5 text-right font-mono text-amber-300 font-semibold">{china_avg_yield:.2f}%</td>
                            <td class="p-3.5 text-right font-mono font-bold text-emerald-400 text-sm">+{china_avg_drip:.2f}%</td>
                            <td class="p-3.5 text-right font-mono text-slate-300">+{china_avg_nondrip:.2f}%</td>
                            <td class="p-3.5 text-right font-mono text-indigo-300 font-semibold">+{china_avg_drip-china_avg_nondrip:.2f}%/年</td>
                            <td class="p-3.5 text-slate-300 leading-relaxed text-xs">
                                长江电力 (99.5%)、中国神华 (97.9%)、中国移动 (97.8%)、招商银行 (97.8%)、贵州茅台 (97.2%)、工商银行 (96.2%)、陕西煤业 (100%)、中国核电 (100%)、宝丰能源 (100%)、华能水电 (99.5%)
                            </td>
                        </tr>
                        <tr class="hover:bg-slate-800/40 transition">
                            <td class="p-3.5 font-bold text-amber-400 flex items-center gap-2 whitespace-nowrap">
                                <span class="w-2.5 h-2.5 rounded-full bg-amber-400"></span> 特定区域生意 (Regional Monopoly)
                            </td>
                            <td class="p-3.5 text-center font-semibold text-white">{region_count} 家 ({region_count/total_stocks*100:.1f}%)</td>
                            <td class="p-3.5 text-right font-mono">{region_cap:,.0f}</td>
                            <td class="p-3.5 text-right font-mono text-slate-400">0.0% (国内 100%)</td>
                            <td class="p-3.5 text-right font-mono font-bold text-amber-400">{region_avg_yield:.2f}%</td>
                            <td class="p-3.5 text-right font-mono font-bold text-emerald-400 text-sm">+{region_avg_drip:.2f}% (最高)</td>
                            <td class="p-3.5 text-right font-mono text-slate-300">+{region_avg_nondrip:.2f}%</td>
                            <td class="p-3.5 text-right font-mono font-bold text-indigo-300">+{region_avg_drip-region_avg_nondrip:.2f}%/年</td>
                            <td class="p-3.5 text-slate-300 leading-relaxed text-xs">
                                宁沪高速 (江苏长三角黄金通道100%)、深高速 (深圳及大湾区路桥100%)、粤高速A (粤港澳大湾区高速100%)
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>

            <!-- Deep Dive Text Cards on 3 Scopes -->
            <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div class="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-3 hover:border-sky-500/50 transition shadow-md">
                    <div class="flex items-center justify-between">
                        <span class="px-2.5 py-1 text-xs font-semibold rounded bg-sky-500/20 text-sky-400 border border-sky-500/30">
                            全球生意模式 (12家)
                        </span>
                        <span class="text-xs text-slate-400 font-mono">平均海外占比 {global_avg_overseas:.1f}%</span>
                    </div>
                    <h4 class="text-base font-bold text-white">跨国供应链整合与全球市占率引领</h4>
                    <p class="text-xs text-slate-300 leading-relaxed">
                        入选企业具备深厚的<strong>跨国本土化制造、海外矿山资源开发、全球分销与OEM深度绑定</strong>。例如紫金矿业海外铜金矿山贡献超四成利润；福耀玻璃在美欧拥有本地化汽车玻璃工厂；工业富联为北美AI云厂商提供全球服务器制造；华利集团在越南、印尼拥有庞大鞋履代工基地。
                    </p>
                    <div class="border-t border-slate-800 pt-2 text-[11px] text-slate-400">
                        <span class="font-semibold text-slate-300">宏观与地缘对冲：</span>能有效分散单一国内宏观周期波动，享有海外通胀提价与汇兑收益；但面临贸易关税政策扰动与出口合规审查。
                    </div>
                </div>

                <div class="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-3 hover:border-emerald-500/50 transition shadow-md">
                    <div class="flex items-center justify-between">
                        <span class="px-2.5 py-1 text-xs font-semibold rounded bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
                            大部分业务在中国 (32家)
                        </span>
                        <span class="text-xs text-slate-400 font-mono">总市值 24.77 万亿 (占89.9%)</span>
                    </div>
                    <h4 class="text-base font-bold text-white">14亿人口大内循环基础设施与垄断特许</h4>
                    <p class="text-xs text-slate-300 leading-relaxed">
                        占据持续分红标的的绝对中枢。依托中国超大规模市场、不可复制的自然禀赋与国家战略基础设施。长江电力掌控三峡等六座超级梯级水电站；中国神华掌控煤电运一体化；中国核电拥有国家特许运营双寡头牌照；三大电信运营商与四大国有行构筑数字与金融动脉。
                    </p>
                    <div class="border-t border-slate-800 pt-2 text-[11px] text-slate-400">
                        <span class="font-semibold text-slate-300">宏观与地缘对冲：</span>完全免疫外部贸易关税与长臂管辖，现金流极度透明确定，主权信用评级强韧；受国内信贷与内需消费倾向主导。
                    </div>
                </div>

                <div class="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-3 hover:border-amber-500/50 transition shadow-md">
                    <div class="flex items-center justify-between">
                        <span class="px-2.5 py-1 text-xs font-semibold rounded bg-amber-500/20 text-amber-400 border border-amber-500/30">
                            特定区域生意 (3家)
                        </span>
                        <span class="text-xs text-amber-400 font-mono">平均DRIP年化 +{region_avg_drip:.2f}% (第一)</span>
                    </div>
                    <h4 class="text-base font-bold text-white">黄金经济动脉与极致现金分红提款机</h4>
                    <p class="text-xs text-slate-300 leading-relaxed">
                        核心资产100%位于中国经济最活跃、车流量最饱和的地理大动脉。宁沪高速扼守长三角上海至南京黄金通道；粤高速A与深高速牢牢掌控粤港澳大湾区核心高速路网。路桥资产基本完成早期高资本开支折旧，净现金流转化率超100%。
                    </p>
                    <div class="border-t border-slate-800 pt-2 text-[11px] text-slate-400">
                        <span class="font-semibold text-slate-300">宏观与地缘对冲：</span>分红率普遍超70%，平均股息率达5.62%，近5年 DRIP 复合年化高达 +14.17%，是稳健防守投资者的极佳复利标的。
                    </div>
                </div>
            </div>
        </section>
""")

# Section 2: Market Cap Stats (>= 200亿)
parts.append(f"""
        <!-- Section 2: 市值全景统计与结构分级画像 (≥200亿) -->
        <section id="marketcap-stats" class="space-y-6 pt-4">
            <div class="flex flex-wrap items-center justify-between border-b border-slate-800 pb-3 gap-2">
                <div>
                    <h3 class="text-xl font-bold text-white flex items-center gap-2">
                        <span class="text-sky-400">▌ 专题项 2</span> 市值全景统计与层级分布画像 (≥200亿全勤样本)
                    </h3>
                    <p class="text-xs sm:text-sm text-slate-400 mt-1">
                        深入统计200亿市值以上全勤样本的市值规模、阶梯分布、集中度及股息率相关性。
                    </p>
                </div>
                <span class="text-xs px-3 py-1 rounded bg-slate-800 text-slate-300 border border-slate-700 font-mono">
                    均值: {avg_cap:,.0f} 亿 · 中位数: {median_cap:,.0f} 亿
                </span>
            </div>

            <!-- 4 Tiers Grid for >= 200亿 -->
            <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                <div class="bg-slate-900 border border-slate-800 rounded-xl p-4 text-center hover:border-purple-500/50 transition">
                    <span class="text-xs font-semibold px-2 py-0.5 rounded bg-purple-500/20 text-purple-300 border border-purple-500/30">万亿超级巨头 (≥10,000亿)</span>
                    <div class="text-2xl font-bold text-white mt-2">{len(tier_mega)} <span class="text-xs font-normal text-slate-400">家</span></div>
                    <div class="text-xs text-slate-300 mt-1">合计: {sum(s['market_cap'] for s in tier_mega):,.0f} 亿</div>
                    <div class="text-[11px] text-purple-400 mt-1 font-semibold">市值占比: {sum(s['market_cap'] for s in tier_mega)/total_cap*100:.1f}%</div>
                    <div class="text-[11px] text-slate-400 mt-2 border-t border-slate-800 pt-1 text-left leading-relaxed">
                        工商银行、中国移动、建设银行、贵州茅台、农业银行、中国石油、中国银行、中国海油
                    </div>
                </div>

                <div class="bg-slate-900 border border-slate-800 rounded-xl p-4 text-center hover:border-sky-500/50 transition">
                    <span class="text-xs font-semibold px-2 py-0.5 rounded bg-sky-500/20 text-sky-300 border border-sky-500/30">超大盘核心 (3,000-10,000亿)</span>
                    <div class="text-2xl font-bold text-white mt-2">{len(tier_large)} <span class="text-xs font-normal text-slate-400">家</span></div>
                    <div class="text-xs text-slate-300 mt-1">合计: {sum(s['market_cap'] for s in tier_large):,.0f} 亿</div>
                    <div class="text-[11px] text-sky-400 mt-1 font-semibold">市值占比: {sum(s['market_cap'] for s in tier_large)/total_cap*100:.1f}%</div>
                    <div class="text-[11px] text-slate-400 mt-2 border-t border-slate-800 pt-1 text-left leading-relaxed">
                        招行、神华、宁德时代、平安、中石化、长电、电信、交行、五粮液、美的、邮储、工业富联、紫金矿业、迈瑞
                    </div>
                </div>

                <div class="bg-slate-900 border border-slate-800 rounded-xl p-4 text-center hover:border-emerald-500/50 transition">
                    <span class="text-xs font-semibold px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">大盘领军白马 (1,000-3,000亿)</span>
                    <div class="text-2xl font-bold text-white mt-2">{len(tier_mid)} <span class="text-xs font-normal text-slate-400">家</span></div>
                    <div class="text-xs text-slate-300 mt-1">合计: {sum(s['market_cap'] for s in tier_mid):,.0f} 亿</div>
                    <div class="text-[11px] text-emerald-400 mt-1 font-semibold">市值占比: {sum(s['market_cap'] for s in tier_mid)/total_cap*100:.1f}%</div>
                    <div class="text-[11px] text-slate-400 mt-2 border-t border-slate-800 pt-1 text-left leading-relaxed">
                        恒瑞、海康、汾酒、陕煤、中建、海天、中国核电、宝丰能源、华能水电、伊利、福耀、大秦、药明、片仔癀
                    </div>
                </div>

                <div class="bg-slate-900 border border-slate-800 rounded-xl p-4 text-center hover:border-amber-500/50 transition">
                    <span class="text-xs font-semibold px-2 py-0.5 rounded bg-amber-500/20 text-amber-300 border border-amber-500/30">中大盘高息绩优 (200-1,000亿)</span>
                    <div class="text-2xl font-bold text-white mt-2">{len(tier_growth)} <span class="text-xs font-normal text-slate-400">家</span></div>
                    <div class="text-xs text-slate-300 mt-1">合计: {sum(s['market_cap'] for s in tier_growth):,.0f} 亿</div>
                    <div class="text-[11px] text-amber-400 mt-1 font-semibold">平均股息率: 5.61%</div>
                    <div class="text-[11px] text-slate-400 mt-2 border-t border-slate-800 pt-1 text-left leading-relaxed">
                        双汇发展、华利集团、宁沪高速、华东医药、东阿阿胶、三七互娱、玲珑轮胎、达仁堂、深高速、粤高速A、江铃汽车
                    </div>
                </div>
            </div>

            <!-- Deep Statistical Insights -->
            <div class="bg-slate-900/60 border border-slate-800 rounded-xl p-5 space-y-3 text-xs sm:text-sm text-slate-300">
                <h4 class="font-bold text-white flex items-center gap-2">
                    <span class="text-sky-400">📊</span> 200亿+ 市值门槛过滤后的关键量化特征
                </h4>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4 leading-relaxed">
                    <div>
                        <strong class="text-slate-100">1. 流动性与机构定价权压舱石：</strong>
                        总市值达到 27.55 万亿元，在过滤掉微盘小市值股票后，该组合完全由公募基金重仓、保险资金底仓以及外资陆股通的核心标的构成。标的换手率适中，冲击成本极低，适合容纳大规模配置资金。
                    </div>
                    <div>
                        <strong class="text-slate-100">2. 剔除科创板与北交所后的估值安全性：</strong>
                        主板与创业板大中盘分红股的盈利成熟度更高，几乎全部跨越了早期研发与重资产扩张的高风险期。自由现金流充沛度更高，平均股息率达到 4.55%，显著超越 10 年期国债无风险收益率。
                    </div>
                </div>
            </div>
        </section>
""")

# Section 3: 5Y Compound Return DRIP vs Non-DRIP
parts.append(f"""
        <!-- Section 3: 近5年复合年化（DRIP vs 非DRIP）复利价值深度解构 -->
        <section id="drip-analysis" class="space-y-6 pt-4">
            <div class="flex flex-wrap items-center justify-between border-b border-slate-800 pb-3 gap-2">
                <div>
                    <h3 class="text-xl font-bold text-white flex items-center gap-2">
                        <span class="text-sky-400">▌ 专题项 3</span> 近5年复合年化回报测算：DRIP（分红再投资）vs 不drip（纯价格回报）
                    </h3>
                    <p class="text-xs sm:text-sm text-slate-400 mt-1">
                        严格针对用户要求的“近5年的复合年化：分为drip和不drip。如果是上市不到5年，在这一点中也继续统计”。
                    </p>
                </div>
                <span class="text-xs px-3 py-1 rounded bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 font-semibold font-mono">
                    样本平均DRIP年化 +{avg_drip:.2f}%
                </span>
            </div>

            <!-- Top 10 DRIP compounders table -->
            <div class="space-y-3">
                <div class="flex items-center justify-between">
                    <div class="text-xs font-semibold text-slate-300">
                        🏆 近5年 DRIP 分红再投资复合年化回报 TOP 10 领军榜 (≥200亿标的)
                    </div>
                    <span class="text-[11px] text-slate-400">注：不足5年者严格按自上市日至今实际持有期年化</span>
                </div>
                <div class="overflow-x-auto rounded-xl border border-slate-800 bg-slate-900/60 shadow">
                    <table class="w-full text-left text-xs sm:text-sm text-slate-300">
                        <thead class="bg-slate-800/80 text-slate-300 text-xs font-semibold uppercase">
                            <tr>
                                <th class="p-3 whitespace-nowrap">排名</th>
                                <th class="p-3 whitespace-nowrap">代码</th>
                                <th class="p-3 whitespace-nowrap">证券简称</th>
                                <th class="p-3 whitespace-nowrap">业务地域</th>
                                <th class="p-3 whitespace-nowrap text-right">总市值(亿元)</th>
                                <th class="p-3 whitespace-nowrap text-right">股息率(TTM)</th>
                                <th class="p-3 whitespace-nowrap text-right text-emerald-400 font-bold">5年 DRIP 复合年化</th>
                                <th class="p-3 whitespace-nowrap text-right">5年 不drip 复合年化</th>
                                <th class="p-3 whitespace-nowrap text-right text-indigo-300">DRIP 超额剪刀差</th>
                                <th class="p-3 whitespace-nowrap">统计期说明</th>
                            </tr>
                        </thead>
                        <tbody class="divide-y divide-slate-800">
""")

for idx, s in enumerate(top_drip):
    scope_badge_class = (
        'bg-sky-500/20 text-sky-400 border border-sky-500/30' if s['business_scope']=='全球生意' else
        ('bg-amber-500/20 text-amber-400 border border-amber-500/30' if s['business_scope']=='特定区域生意' else 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30')
    )
    tenure_badge = f"<span class='text-amber-400 font-semibold'>上市{s['actual_years_calculated']:.1f}年(实际年化)</span>" if s['is_less_than_5y'] else f"满5年(上市{s['continuous_div_years']}年)"
    spread = s['cagr_5y_drip'] - s['cagr_5y_non_drip']
    parts.append(f"""
                            <tr class="hover:bg-slate-800/40 transition">
                                <td class="p-3 font-bold text-amber-400">#{idx+1}</td>
                                <td class="p-3 font-mono">{s['code']}</td>
                                <td class="p-3 font-bold text-white whitespace-nowrap">{s['name']}</td>
                                <td class="p-3 whitespace-nowrap"><span class="px-2 py-0.5 rounded text-[11px] {scope_badge_class}">{s['business_scope']}</span></td>
                                <td class="p-3 text-right font-mono">{s['market_cap']:,.0f}</td>
                                <td class="p-3 text-right text-amber-300 font-semibold font-mono">{s['dividend_yield']:.2f}%</td>
                                <td class="p-3 text-right font-bold text-emerald-400 text-sm font-mono">+{s['cagr_5y_drip']:.2f}%</td>
                                <td class="p-3 text-right text-slate-300 font-mono">+{s['cagr_5y_non_drip']:.2f}%</td>
                                <td class="p-3 text-right font-semibold text-indigo-300 font-mono">+{spread:.2f}%/年</td>
                                <td class="p-3 text-xs text-slate-400 whitespace-nowrap">{tenure_badge}</td>
                            </tr>
    """)

parts.append(f"""
                        </tbody>
                    </table>
                </div>
            </div>

            <!-- Compounding Simulation Tool -->
            <div class="bg-gradient-to-r from-slate-900 via-indigo-950/40 to-slate-900 border border-indigo-900/40 rounded-2xl p-6 space-y-4 shadow-xl">
                <div class="flex flex-wrap items-center justify-between gap-3">
                    <div>
                        <h4 class="text-base font-bold text-white flex items-center gap-2">
                            <span>🧮</span> 交互式 DRIP 复利“滚雪球”财富效应模拟器
                        </h4>
                        <p class="text-xs text-slate-300 mt-0.5">
                            测算在200亿+全勤样本均值收益率（DRIP +9.61% vs 非DRIP +5.29%）下，分红再投资相比不复投产生的财富差异。
                        </p>
                    </div>
                    <div class="flex flex-wrap items-center gap-3">
                        <label class="text-xs text-slate-300">初始本金 (元):
                            <input type="number" id="calcPrincipal" value="100000" step="10000" min="10000" class="ml-1 w-28 px-2 py-1 text-xs bg-slate-800 border border-slate-700 rounded text-white font-mono">
                        </label>
                        <label class="text-xs text-slate-300">投资年限 (年):
                            <select id="calcYears" class="ml-1 px-2 py-1 text-xs bg-slate-800 border border-slate-700 rounded text-white">
                                <option value="3">3 年</option>
                                <option value="5" selected>5 年</option>
                                <option value="10">10 年</option>
                                <option value="15">15 年</option>
                                <option value="20">20 年</option>
                            </select>
                        </label>
                        <button onclick="calculateDRIPCompounding()" class="px-3.5 py-1.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-xs font-semibold transition shadow">
                            测算终值
                        </button>
                    </div>
                </div>

                <div class="grid grid-cols-1 sm:grid-cols-3 gap-4 pt-2">
                    <div class="bg-slate-900/80 border border-slate-800 rounded-xl p-4 text-center">
                        <div class="text-xs text-slate-400">不复投 (Non-DRIP) 资产终值</div>
                        <div id="resNonDRIP" class="text-xl font-bold text-slate-200 mt-1 font-mono">¥ 129,400</div>
                        <div id="resNonDRIPGain" class="text-[11px] text-slate-400 mt-0.5">累计总收益: +29.4%</div>
                    </div>
                    <div class="bg-slate-900/80 border border-indigo-700/50 rounded-xl p-4 text-center">
                        <div class="text-xs text-indigo-300 font-semibold">DRIP 分红再投资 资产终值</div>
                        <div id="resDRIP" class="text-xl font-bold text-emerald-400 mt-1 font-mono">¥ 158,210</div>
                        <div id="resDRIPGain" class="text-[11px] text-emerald-400 mt-0.5 font-semibold">累计总收益: +58.2%</div>
                    </div>
                    <div class="bg-slate-900/80 border border-emerald-700/50 rounded-xl p-4 text-center">
                        <div class="text-xs text-emerald-300 font-semibold">DRIP 创造的超额财富净增量</div>
                        <div id="resExcess" class="text-xl font-bold text-indigo-300 mt-1 font-mono">+¥ 28,810</div>
                        <div id="resExcessRatio" class="text-[11px] text-indigo-300 mt-0.5 font-semibold">净收益高出 98.0%</div>
                    </div>
                </div>
            </div>
        </section>
""")

# Section 4: Sub-5 Years
parts.append(f"""
        <!-- Section 4: 上市不足5年次新全勤股专项统计 (≥200亿) -->
        <section id="sub5y-stocks" class="space-y-6 pt-4">
            <div class="flex flex-wrap items-center justify-between border-b border-slate-800 pb-3 gap-2">
                <div>
                    <h3 class="text-xl font-bold text-white flex items-center gap-2">
                        <span class="text-sky-400">▌ 专题项 4</span> 上市不足5年次新全勤分红样本专项统计 (实际持有期折算年化)
                    </h3>
                    <p class="text-xs sm:text-sm text-slate-400 mt-1">
                        严格落实用户要求：<strong>“第1点中提到的，如果是上市不到5年，在这一点中也继续统计”</strong>。在≥200亿市值区间内共有3家，自上市日至今实际年限折算复合年化 CAGR。
                    </p>
                </div>
                <span class="text-xs px-3 py-1 rounded bg-amber-500/20 text-amber-400 border border-amber-500/30 font-mono">
                    3只次新200亿+全勤标的
                </span>
            </div>

            <!-- Sub 5y Table -->
            <div class="overflow-x-auto rounded-xl border border-slate-800 bg-slate-900/60 shadow-lg">
                <table class="w-full text-left text-xs sm:text-sm text-slate-300">
                    <thead class="bg-slate-800 text-slate-200 text-xs font-semibold uppercase tracking-wider">
                        <tr>
                            <th class="p-3.5 whitespace-nowrap">代码</th>
                            <th class="p-3.5 whitespace-nowrap">简称</th>
                            <th class="p-3.5 whitespace-nowrap">所属行业</th>
                            <th class="p-3.5 whitespace-nowrap">上市日期</th>
                            <th class="p-3.5 whitespace-nowrap text-center">实际上市年限</th>
                            <th class="p-3.5 whitespace-nowrap text-right">总市值(亿元)</th>
                            <th class="p-3.5 whitespace-nowrap text-right">股息率(TTM)</th>
                            <th class="p-3.5 whitespace-nowrap text-right text-emerald-400 font-bold">实际年化 DRIP 回报</th>
                            <th class="p-3.5 whitespace-nowrap text-right">实际年化 非DRIP 回报</th>
                            <th class="p-3.5 whitespace-nowrap">业务地域类型</th>
                            <th class="p-3.5 whitespace-nowrap text-right">海外占比</th>
                            <th class="p-3.5 min-w-[280px]">次新全勤与分红持续性保障点评</th>
                        </tr>
                    </thead>
                    <tbody class="divide-y divide-slate-800">
""")

for s in sub5y_list:
    scope_badge_class = 'bg-sky-500/20 text-sky-400 border border-sky-500/30' if s['business_scope']=='全球生意' else 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
    parts.append(f"""
                        <tr class="hover:bg-slate-800/40 transition">
                            <td class="p-3.5 font-mono text-sky-400 font-semibold whitespace-nowrap">{s['code']}</td>
                            <td class="p-3.5 font-bold text-white whitespace-nowrap">{s['name']}</td>
                            <td class="p-3.5 text-slate-300 text-xs whitespace-nowrap">{s['industry']}</td>
                            <td class="p-3.5 font-mono text-slate-400 text-xs whitespace-nowrap">{s['listing_date']}</td>
                            <td class="p-3.5 text-center font-bold text-amber-400 whitespace-nowrap font-mono">{s['actual_years_calculated']:.1f} 年</td>
                            <td class="p-3.5 text-right font-semibold text-white whitespace-nowrap font-mono">{s['market_cap']:,.0f}</td>
                            <td class="p-3.5 text-right text-amber-300 font-semibold whitespace-nowrap font-mono">{s['dividend_yield']:.2f}%</td>
                            <td class="p-3.5 text-right font-bold text-emerald-400 whitespace-nowrap font-mono text-sm">+{s['cagr_5y_drip']:.2f}%</td>
                            <td class="p-3.5 text-right text-slate-300 whitespace-nowrap font-mono">+{s['cagr_5y_non_drip']:.2f}%</td>
                            <td class="p-3.5 whitespace-nowrap"><span class="px-2 py-0.5 rounded text-[11px] {scope_badge_class}">{s['business_scope']}</span></td>
                            <td class="p-3.5 text-right font-semibold text-sky-300 whitespace-nowrap font-mono">{s['overseas_rev_pct']:.1f}%</td>
                            <td class="p-3.5 text-xs text-slate-300 leading-relaxed">{s['div_policy']}</td>
                        </tr>
    """)

parts.append(f"""
                    </tbody>
                </table>
            </div>
            <div class="text-xs text-slate-400 bg-slate-900/60 p-4 rounded-xl border border-slate-800 leading-relaxed">
                <strong>📌 次新高市值标的深度点评：</strong>
                中国移动与中国海油分别于2022年初回归A股IPO，上市以来均维持了100%全勤分红（含年中与年度派现），派现规模超千亿，且上市以来的年化复合回报分别高达 22.9% 与 32.8%；华利集团作为全球第二大运动鞋履制造龙头，生产基地布局于越南和印尼，客户全部为全球跨国巨头，上市4年分红率持续稳定在60%以上。
            </div>
        </section>
""")

# Section 5: Master Table & Interactive Engine
parts.append(f"""
        <!-- Section 5: 全维度交互式检索与数据中心 (47只) -->
        <section id="data-table-section" class="space-y-6 pt-4">
            <div class="flex flex-wrap items-center justify-between border-b border-slate-800 pb-3 gap-3">
                <div>
                    <h3 class="text-xl font-bold text-white flex items-center gap-2">
                        <span class="text-sky-400">▌ 全景数据中心</span> A股持续分红全勤个股全维度数据库 (市值≥200亿 · 47只)
                    </h3>
                    <p class="text-xs sm:text-sm text-slate-400 mt-1">
                        已剔除北交所与科创板688，市值全部在200亿元以上。支持多条件复合筛选、关键字搜索与动态多列排序。
                    </p>
                </div>
                <div class="text-xs text-slate-400 bg-slate-800 px-3 py-1.5 rounded-lg border border-slate-700">
                    当前匹配: <span id="matchCount" class="font-bold text-sky-400">{total_stocks}</span> / {total_stocks} 家
                </div>
            </div>

            <!-- Filter Controls Panel -->
            <div id="filter-panel" class="bg-slate-900/90 border border-slate-800 rounded-2xl p-5 space-y-4">
                <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3">
                    <div>
                        <label class="block text-xs font-semibold text-slate-300 mb-1">🔍 关键字模糊检索</label>
                        <input type="text" id="searchInput" oninput="filterTable()" placeholder="搜代码/名称/行业/护城河..." class="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-lg text-xs text-white placeholder-slate-500 focus:outline-none focus:border-sky-500">
                    </div>

                    <div>
                        <label class="block text-xs font-semibold text-slate-300 mb-1">🌍 业务地域类型</label>
                        <select id="scopeFilter" onchange="filterTable()" class="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-lg text-xs text-white focus:outline-none focus:border-sky-500">
                            <option value="ALL">全部地域类型</option>
                            <option value="全球生意">全球生意 (海外占比高)</option>
                            <option value="全国大部分在中国">全国大部分业务在中国</option>
                            <option value="特定区域生意">特定区域垄断生意</option>
                        </select>
                    </div>

                    <div>
                        <label class="block text-xs font-semibold text-slate-300 mb-1">💰 市值规模梯队</label>
                        <select id="capTierFilter" onchange="filterTable()" class="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-lg text-xs text-white focus:outline-none focus:border-sky-500">
                            <option value="ALL">全部市值规模 (≥200亿)</option>
                            <option value="MEGA">万亿级超级巨头 (≥10,000亿)</option>
                            <option value="LARGE">超大盘核心 (3,000-10,000亿)</option>
                            <option value="MID">大盘领军白马 (1,000-3,000亿)</option>
                            <option value="GROWTH">中大盘高息绩优 (200-1,000亿)</option>
                        </select>
                    </div>

                    <div>
                        <label class="block text-xs font-semibold text-slate-300 mb-1">⏳ 上市年限过滤</label>
                        <select id="listingFilter" onchange="filterTable()" class="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-lg text-xs text-white focus:outline-none focus:border-sky-500">
                            <option value="ALL">全部上市年限</option>
                            <option value="GTE5">满 5 年以上</option>
                            <option value="LT5">上市不足 5 年 (次新样本)</option>
                        </select>
                    </div>

                    <div>
                        <label class="block text-xs font-semibold text-slate-300 mb-1">🎖️ 连续分红年限</label>
                        <select id="yearsFilter" onchange="filterTable()" class="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-lg text-xs text-white focus:outline-none focus:border-sky-500">
                            <option value="ALL">全部连续年限</option>
                            <option value="25PLUS">25 年以上 (老牌常青藤)</option>
                            <option value="15TO24">15 - 24 年 (成熟核心标杆)</option>
                            <option value="5TO14">5 - 14 年 (稳健高分红)</option>
                            <option value="LT5">&lt; 5 年 (全勤新秀)</option>
                        </select>
                    </div>
                </div>

                <div class="flex justify-between items-center pt-2 border-t border-slate-800/80 text-xs">
                    <span class="text-slate-400">💡 提示：点击表头可进行升序/降序排列；支持横向左右滚动。</span>
                    <button onclick="resetFilters()" class="text-sky-400 hover:text-sky-300 transition font-semibold">重置筛选条件</button>
                </div>
            </div>

            <!-- Master Table Container -->
            <div class="overflow-x-auto rounded-2xl border border-slate-800 bg-slate-900/70 shadow-2xl">
                <table id="stocksTable" class="w-full text-left text-xs sm:text-sm text-slate-300">
                    <thead class="bg-slate-800 text-slate-200 text-xs uppercase font-semibold tracking-wider sticky top-16 z-20">
                        <tr>
                            <th onclick="sortTable(0, 'str')" class="p-3.5 cursor-pointer hover:bg-slate-700 transition sort-icon whitespace-nowrap">代码</th>
                            <th onclick="sortTable(1, 'str')" class="p-3.5 cursor-pointer hover:bg-slate-700 transition sort-icon whitespace-nowrap">证券简称</th>
                            <th onclick="sortTable(2, 'str')" class="p-3.5 cursor-pointer hover:bg-slate-700 transition sort-icon whitespace-nowrap">申万行业</th>
                            <th onclick="sortTable(3, 'str')" class="p-3.5 cursor-pointer hover:bg-slate-700 transition sort-icon whitespace-nowrap">上市日期</th>
                            <th onclick="sortTable(4, 'num')" class="p-3.5 cursor-pointer hover:bg-slate-700 transition sort-icon whitespace-nowrap text-center">连续分红年限</th>
                            <th onclick="sortTable(5, 'num')" class="p-3.5 cursor-pointer hover:bg-slate-700 transition sort-icon whitespace-nowrap text-right">总市值(亿)</th>
                            <th onclick="sortTable(6, 'num')" class="p-3.5 cursor-pointer hover:bg-slate-700 transition sort-icon whitespace-nowrap text-right">股息率(%)</th>
                            <th onclick="sortTable(7, 'num')" class="p-3.5 cursor-pointer hover:bg-slate-700 transition sort-icon whitespace-nowrap text-right">5年非DRIP年化</th>
                            <th onclick="sortTable(8, 'num')" class="p-3.5 cursor-pointer hover:bg-slate-700 transition sort-icon whitespace-nowrap text-right text-emerald-400">5年DRIP年化</th>
                            <th onclick="sortTable(9, 'num')" class="p-3.5 cursor-pointer hover:bg-slate-700 transition sort-icon whitespace-nowrap text-right text-indigo-300">DRIP超额</th>
                            <th onclick="sortTable(10, 'str')" class="p-3.5 cursor-pointer hover:bg-slate-700 transition sort-icon whitespace-nowrap">业务地域类型</th>
                            <th onclick="sortTable(11, 'num')" class="p-3.5 cursor-pointer hover:bg-slate-700 transition sort-icon whitespace-nowrap text-right">海外占比</th>
                            <th class="p-3.5 min-w-[280px]">商业模式护城河与区域/全球属性深度点评</th>
                        </tr>
                    </thead>
                    <tbody id="stocksTableBody" class="divide-y divide-slate-800">
                        <!-- Populated by JavaScript -->
                    </tbody>
                </table>
            </div>
        </section>

        <!-- Section 6: 机构研判与资产配置策略 -->
        <section class="bg-gradient-to-br from-slate-900 via-slate-900 to-indigo-950/40 border border-slate-800 rounded-2xl p-6 sm:p-8 space-y-6">
            <h3 class="text-xl font-bold text-white flex items-center gap-2">
                <span class="text-sky-400">▌ 总结与投资启示</span> 持续分红核心资产的配置哲学与核心结论
            </h3>

            <div class="grid grid-cols-1 md:grid-cols-3 gap-6 text-xs sm:text-sm text-slate-300 leading-relaxed">
                <div class="bg-slate-850/60 p-5 rounded-xl border border-slate-800 space-y-2">
                    <h4 class="font-bold text-white flex items-center gap-1.5">
                        <span class="text-emerald-400">1.</span> “分红全勤 + 200亿市值”铸造最高确定性
                    </h4>
                    <p>
                        将市值门槛设定在200亿元并剔除北交所与科创板，过滤掉了高研发不确定性与微盘投机流动性风险。入选的47只核心资产总市值达到27.55万亿元，展现了极强的商业成熟度、充裕的自由现金流和坚决履行股东回报的治理契约。
                    </p>
                </div>

                <div class="bg-slate-850/60 p-5 rounded-xl border border-slate-800 space-y-2">
                    <h4 class="font-bold text-white flex items-center gap-1.5">
                        <span class="text-sky-400">2.</span> DRIP 是长期复利的核心引擎
                    </h4>
                    <p>
                        统计数据显示，近5年DRIP全收益年化平均达9.61%，相比非DRIP年化的5.29%产生了+4.32%/年的超额复利。在市场弱势震荡时，分红再投资能够以低估值持续吸纳更多廉价股份，当均值回归来临时，实现持股数量与股价的双重戴维斯双击。
                    </p>
                </div>

                <div class="bg-slate-850/60 p-5 rounded-xl border border-slate-800 space-y-2">
                    <h4 class="font-bold text-white flex items-center gap-1.5">
                        <span class="text-indigo-400">3.</span> “全球资源制造龙头 + 国内垄断印钞机”哑铃配置
                    </h4>
                    <p>
                        建议构建“两极平衡哑铃”：一端重仓大部分业务在中国的公用事业与国家能源资产（长江电力、中国神华、华能水电、中国核电、四大行），获取类永续债的高确定性现金流；另一端精选海外业务占比高、具备全球定价权的矿产与制造领航者（紫金矿业、福耀玻璃、工业富联、宁德时代），分享全球工业红利。
                    </p>
                </div>
            </div>
        </section>

    </main>

    <!-- Footer -->
    <footer class="border-t border-slate-800 bg-slate-900/80 py-8 text-center text-xs text-slate-500">
        <div class="max-w-7xl mx-auto px-4 space-y-2">
            <p>A股上市以来持续分红全勤标的深度研报 (市值≥200亿 · 排除北交所/688) · 数据基准日：2026年9月</p>
            <p>免责声明：本数据报表及量化统计仅供金融学术研究与策略回测参考，不构成任何直接投资建议与买卖推荐。</p>
        </div>
    </footer>

    <!-- Embedded Raw Data & Client-side Engine -->
    <script>
        const STOCKS_DATA = {json.dumps(stocks, ensure_ascii=False)};

        let currentFilteredData = [...STOCKS_DATA];
        let currentSortColumn = 5; // Default sort by Market Cap
        let currentSortAsc = false; // Descending

        function renderTable(data) {{
            const tbody = document.getElementById('stocksTableBody');
            tbody.innerHTML = '';

            data.forEach((s) => {{
                const tr = document.createElement('tr');
                tr.className = 'hover:bg-slate-800/40 transition';

                let scopeBadge = '';
                if (s.business_scope === '全球生意') {{
                    scopeBadge = '<span class="px-2 py-0.5 rounded text-[11px] font-medium bg-sky-500/20 text-sky-400 border border-sky-500/30">全球生意</span>';
                }} else if (s.business_scope === '特定区域生意') {{
                    scopeBadge = '<span class="px-2 py-0.5 rounded text-[11px] font-medium bg-amber-500/20 text-amber-400 border border-amber-500/30">特定区域生意</span>';
                }} else {{
                    scopeBadge = '<span class="px-2 py-0.5 rounded text-[11px] font-medium bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">国内大盘</span>';
                }}

                const dripColor = s.cagr_5y_drip >= 10 ? 'text-emerald-400 font-bold' : (s.cagr_5y_drip > 0 ? 'text-emerald-300' : 'text-rose-400');
                const nonDripColor = s.cagr_5y_non_drip >= 10 ? 'text-slate-100 font-semibold' : (s.cagr_5y_non_drip > 0 ? 'text-slate-300' : 'text-rose-400');
                const spread = (s.cagr_5y_drip - s.cagr_5y_non_drip).toFixed(2);

                const sub5yTag = s.is_less_than_5y 
                    ? `<span class="ml-1 text-[10px] bg-amber-500/20 text-amber-300 px-1 py-0.5 rounded border border-amber-500/30 font-semibold" title="自上市以来实际年化">上市${{s.actual_years_calculated}}年</span>`
                    : '';

                tr.innerHTML = `
                    <td class="p-3.5 font-mono text-sky-400 font-medium whitespace-nowrap">${{s.code}}</td>
                    <td class="p-3.5 font-bold text-white whitespace-nowrap">${{s.name}}${{sub5yTag}}</td>
                    <td class="p-3.5 text-slate-300 text-xs whitespace-nowrap">${{s.industry}}</td>
                    <td class="p-3.5 font-mono text-slate-400 text-xs whitespace-nowrap">${{s.listing_date}}</td>
                    <td class="p-3.5 text-center font-bold text-amber-300 whitespace-nowrap font-mono">${{s.continuous_div_years}} 年</td>
                    <td class="p-3.5 text-right font-semibold text-white whitespace-nowrap font-mono">${{s.market_cap.toLocaleString('en-US', {{minimumFractionDigits: 0, maximumFractionDigits: 1}})}}</td>
                    <td class="p-3.5 text-right text-amber-400 font-semibold whitespace-nowrap font-mono">${{s.dividend_yield.toFixed(2)}}%</td>
                    <td class="p-3.5 text-right ${{nonDripColor}} whitespace-nowrap font-mono">${{s.cagr_5y_non_drip > 0 ? '+' : ''}}${{s.cagr_5y_non_drip.toFixed(2)}}%</td>
                    <td class="p-3.5 text-right ${{dripColor}} whitespace-nowrap font-mono text-sm">${{s.cagr_5y_drip > 0 ? '+' : ''}}${{s.cagr_5y_drip.toFixed(2)}}%</td>
                    <td class="p-3.5 text-right text-indigo-300 font-medium whitespace-nowrap font-mono">+${{spread}}%</td>
                    <td class="p-3.5 whitespace-nowrap">${{scopeBadge}}</td>
                    <td class="p-3.5 text-right font-medium text-sky-300 whitespace-nowrap font-mono">${{s.overseas_rev_pct.toFixed(1)}}%</td>
                    <td class="p-3.5 text-xs text-slate-300 leading-relaxed max-w-md">
                        <div class="font-medium text-slate-200 mb-0.5">${{s.business_model_moat}}</div>
                        <div class="text-[11px] text-slate-400">${{s.geography_detail}}</div>
                    </td>
                `;
                tbody.appendChild(tr);
            }});

            document.getElementById('matchCount').innerText = data.length;
        }}

        function filterTable() {{
            const search = document.getElementById('searchInput').value.trim().toLowerCase();
            const scope = document.getElementById('scopeFilter').value;
            const capTier = document.getElementById('capTierFilter').value;
            const listing = document.getElementById('listingFilter').value;
            const years = document.getElementById('yearsFilter').value;

            currentFilteredData = STOCKS_DATA.filter(s => {{
                if (search) {{
                    const matchText = (s.code + ' ' + s.name + ' ' + s.industry + ' ' + s.business_scope + ' ' + s.business_model_moat + ' ' + s.geography_detail).toLowerCase();
                    if (!matchText.includes(search)) return false;
                }}

                if (scope !== 'ALL' && s.business_scope !== scope) return false;

                if (capTier === 'MEGA' && s.market_cap < 10000) return false;
                if (capTier === 'LARGE' && (s.market_cap < 3000 || s.market_cap >= 10000)) return false;
                if (capTier === 'MID' && (s.market_cap < 1000 || s.market_cap >= 3000)) return false;
                if (capTier === 'GROWTH' && (s.market_cap < 200 || s.market_cap >= 1000)) return false;

                if (listing === 'GTE5' && s.is_less_than_5y) return false;
                if (listing === 'LT5' && !s.is_less_than_5y) return false;

                if (years === '25PLUS' && s.continuous_div_years < 25) return false;
                if (years === '15TO24' && (s.continuous_div_years < 15 || s.continuous_div_years >= 25)) return false;
                if (years === '5TO14' && (s.continuous_div_years < 5 || s.continuous_div_years >= 15)) return false;
                if (years === 'LT5' && s.continuous_div_years >= 5) return false;

                return true;
            }});

            applySort();
        }}

        function sortTable(columnIndex, type) {{
            const table = document.getElementById('stocksTable');
            const ths = table.querySelectorAll('th');

            if (currentSortColumn === columnIndex) {{
                currentSortAsc = !currentSortAsc;
            }} else {{
                currentSortColumn = columnIndex;
                currentSortAsc = (type === 'str');
                if (type === 'num') currentSortAsc = false;
            }}

            ths.forEach((th, idx) => {{
                th.classList.remove('sort-asc', 'sort-desc');
                if (idx === columnIndex) {{
                    th.classList.add(currentSortAsc ? 'sort-asc' : 'sort-desc');
                }}
            }});

            applySort();
        }}

        function applySort() {{
            const col = currentSortColumn;
            const asc = currentSortAsc;

            currentFilteredData.sort((a, b) => {{
                let valA, valB;
                switch (col) {{
                    case 0: valA = a.code; valB = b.code; break;
                    case 1: valA = a.name; valB = b.name; break;
                    case 2: valA = a.industry; valB = b.industry; break;
                    case 3: valA = a.listing_date; valB = b.listing_date; break;
                    case 4: valA = a.continuous_div_years; valB = b.continuous_div_years; break;
                    case 5: valA = a.market_cap; valB = b.market_cap; break;
                    case 6: valA = a.dividend_yield; valB = b.dividend_yield; break;
                    case 7: valA = a.cagr_5y_non_drip; valB = b.cagr_5y_non_drip; break;
                    case 8: valA = a.cagr_5y_drip; valB = b.cagr_5y_drip; break;
                    case 9: valA = a.cagr_5y_drip - a.cagr_5y_non_drip; valB = b.cagr_5y_drip - b.cagr_5y_non_drip; break;
                    case 10: valA = a.business_scope; valB = b.business_scope; break;
                    case 11: valA = a.overseas_rev_pct; valB = b.overseas_rev_pct; break;
                    default: valA = a.market_cap; valB = b.market_cap;
                }}

                if (typeof valA === 'string') {{
                    return asc ? valA.localeCompare(valB, 'zh-CN') : valB.localeCompare(valA, 'zh-CN');
                }} else {{
                    return asc ? valA - valB : valB - valA;
                }}
            }});

            renderTable(currentFilteredData);
        }}

        function resetFilters() {{
            document.getElementById('searchInput').value = '';
            document.getElementById('scopeFilter').value = 'ALL';
            document.getElementById('capTierFilter').value = 'ALL';
            document.getElementById('listingFilter').value = 'ALL';
            document.getElementById('yearsFilter').value = 'ALL';
            currentSortColumn = 5;
            currentSortAsc = false;
            filterTable();
        }}

        function calculateDRIPCompounding() {{
            const p = parseFloat(document.getElementById('calcPrincipal').value) || 100000;
            const years = parseInt(document.getElementById('calcYears').value) || 5;

            const nonDripRate = {avg_non_drip:.4f} / 100.0;
            const dripRate = {avg_drip:.4f} / 100.0;

            const endNonDRIP = p * Math.pow(1 + nonDripRate, years);
            const endDRIP = p * Math.pow(1 + dripRate, years);
            const excess = endDRIP - endNonDRIP;

            const gainNonDRIP = ((endNonDRIP - p) / p * 100).toFixed(1);
            const gainDRIP = ((endDRIP - p) / p * 100).toFixed(1);
            const ratio = ((gainDRIP - gainNonDRIP) / gainNonDRIP * 100).toFixed(1);

            document.getElementById('resNonDRIP').innerText = '¥ ' + Math.round(endNonDRIP).toLocaleString();
            document.getElementById('resNonDRIPGain').innerText = `累计总收益: +${{gainNonDRIP}}%`;

            document.getElementById('resDRIP').innerText = '¥ ' + Math.round(endDRIP).toLocaleString();
            document.getElementById('resDRIPGain').innerText = `累计总收益: +${{gainDRIP}}%`;

            document.getElementById('resExcess').innerText = '+¥ ' + Math.round(excess).toLocaleString();
            document.getElementById('resExcessRatio').innerText = `净收益高出 ${{ratio}}%`;
        }}

        function exportCSV() {{
            const csvRows = [];
            const headers = ["代码", "简称", "申万行业", "上市日期", "连续分红年限", "总市值(亿元)", "流通市值(亿元)", "最新股息率(%)", "5年非DRIP年化(%)", "5年DRIP年化(%)", "上市不足5年", "实际折算年限", "业务地域范围", "海外营收占比(%)", "国内营收占比(%)", "地域分布与出海布局", "商业模式与护城河", "分红政策"];
            csvRows.push(headers.join(","));

            STOCKS_DATA.forEach(s => {{
                const row = [
                    s.code,
                    `"${{s.name}}"`,
                    `"${{s.industry}}"`,
                    s.listing_date,
                    s.continuous_div_years,
                    s.market_cap,
                    s.float_cap,
                    s.dividend_yield,
                    s.cagr_5y_non_drip,
                    s.cagr_5y_drip,
                    s.is_less_than_5y ? '是' : '否',
                    s.actual_years_calculated,
                    `"${{s.business_scope}}"`,
                    s.overseas_rev_pct,
                    s.domestic_rev_pct,
                    `"${{s.geography_detail.replace(/"/g, '""')}}"`,
                    `"${{s.business_model_moat.replace(/"/g, '""')}}"`,
                    `"${{s.div_policy.replace(/"/g, '""')}}"`
                ];
                csvRows.push(row.join(","));
            }});

            const csvBlob = new Blob(["\\uFEFF" + csvRows.join("\\n")], {{ type: 'text/csv;charset=utf-8;' }});
            const url = URL.createObjectURL(csvBlob);
            const a = document.createElement('a');
            a.href = url;
            a.download = "A股持续分红全勤股分析报表(200亿+).csv";
            a.click();
            URL.revokeObjectURL(url);
        }}

        function exportJSON() {{
            navigator.clipboard.writeText(JSON.stringify(STOCKS_DATA, null, 2)).then(() => {{
                alert("已成功复制 47 只持续分红全勤股结构化 JSON 数据到剪贴板！");
            }}).catch(() => {{
                alert("复制失败，请直接使用导出 CSV 功能。");
            }});
        }}

        function toggleTheme() {{
            const html = document.documentElement;
            if (html.classList.contains('dark')) {{
                html.classList.remove('dark');
                document.body.classList.remove('bg-slate-950', 'text-slate-100');
                document.body.classList.add('bg-slate-50', 'text-slate-900');
            }} else {{
                html.classList.add('dark');
                document.body.classList.remove('bg-slate-50', 'text-slate-900');
                document.body.classList.add('bg-slate-950', 'text-slate-100');
            }}
        }}

        window.addEventListener('DOMContentLoaded', () => {{
            sortTable(5, 'num');
        }});
    </script>
</body>
</html>
""")

full_html = "".join(parts)
with open("index.html", "w", encoding="utf-8") as f:
    f.write(full_html)

print("Generated index.html successfully with length:", len(full_html))

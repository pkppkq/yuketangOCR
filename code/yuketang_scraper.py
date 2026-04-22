import asyncio
from playwright.async_api import async_playwright
import re
from datetime import datetime

async def extract_yuketang_questions():
    async with async_playwright() as p:
        # 1. 启动浏览器 (根据要求调用火狐浏览器)
        print("正在启动火狐浏览器...")
        try:
            # 调用你刚刚安装的系统火狐浏览器
            browser = await p.firefox.launch(headless=False, executable_path=r"C:\Program Files\Mozilla Firefox\firefox.exe")
        except Exception:
            # 如果路径不对，尝试使用 Playwright 默认的火狐
            browser = await p.firefox.launch(headless=False)
            
        context = await browser.new_context()
        page = await context.new_page()

        # 2. 打开雨课堂网页
        print(">>> 【重要提示】：请务必只在刚才弹出的这个新浏览器窗口中操作！")
        print(">>> 如果你自己手动打开了你平时的 Chrome/Edge，脚本是抓不到的！")
        print(">>> 请在弹出的窗口中扫码登录雨课堂，然后点击进入测试页面。")
        await page.goto("https://www.yuketang.cn/web/?index")

        # 3. 循环抓取逻辑
        print("\n================ 操作指南 ================")
        print("1. 确保在【弹出的浏览器】中，题目已经完全显示出来")
        print("2. 在此终端直接按【回车键】抓取当前屏幕文本")
        print("3. 抓取完成后会自动保存，你可以继续切换下一题，并再次按回车抓取")
        print("4. 想结束时，输入 'q' 并回车即可退出")
        print("==========================================\n")

        import os
        from rapidocr_onnxruntime import RapidOCR

        crawled_output_file = "yuketang_questions_crawled.txt"
        ocr_output_file = "yuketang_questions_ocr.txt"
        count = 1
        
        print("\n正在初始化本地 OCR 引擎...")
        try:
            ocr_engine = RapidOCR()
        except Exception as e:
            print(f"⚠️ OCR 初始化失败: {e}")
            ocr_engine = None

        while True:
            cmd = input(f"[等待中] 准备抓取第 {count} 次，请按回车确认 (输入 'q' 退出): ")
            if cmd.strip().lower() == 'q':
                break
                
            print("正在提取当前页面文本...")
            
            print(f"[调试] 当前 Playwright 共追踪到 {len(context.pages)} 个页面(标签页)。")
            for idx, p in enumerate(context.pages):
                print(f"[调试] 页面 {idx}: {p.url}")
            
            # 1. 找到当前用户真正处于前台（可见）的标签页
            active_page = context.pages[-1]
            for p in context.pages:
                try:
                    if not await p.evaluate("document.hidden"):
                        active_page = p
                        break
                except Exception:
                    pass
            print(f"[调试] 决定抓取页面 URL: {active_page.url}")
            
            # 创建专门放截图的文件夹
            screenshot_dir = "yuketang_screenshots"
            if not os.path.exists(screenshot_dir):
                os.makedirs(screenshot_dir)
                
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            time_str_for_file = datetime.now().strftime("%Y%m%d_%H%M%S")
            screenshot_path = os.path.join(screenshot_dir, f"题目_{count}_{time_str_for_file}.png")

            # 第一步：精准定位“黑框”即幻灯片主体区域 (穿透 iframe)
            js_find_slide_score = """
            () => {
                let bestEl = null;
                let maxScore = -1;
                let winW = window.innerWidth;
                let winH = window.innerHeight;
                
                document.querySelectorAll('div, img, canvas, section, iframe').forEach(el => {
                    let rect = el.getBoundingClientRect();
                    
                    if (rect.width >= 400 && rect.height >= 250) {
                        let area = rect.width * rect.height;
                        let ratio = rect.width / rect.height;
                        let ratioScore = 1.0;
                        
                        // PPT 比例奖励 (极度关键)
                        if (Math.abs(ratio - 16/9) < 0.1 || 
                            Math.abs(ratio - 4/3) < 0.1 || 
                            Math.abs(ratio - 16/10) < 0.1 ||
                            Math.abs(ratio - 3/2) < 0.1) {
                            ratioScore *= 20.0; // 符合比例的容器权重极大！
                        }
                        
                        // 惩罚全屏面板或包含了侧边栏的大外壳
                        // 无论它的比例多么完美（比如用户的整个显示器恰好就是16:9），只要占据了绝大部分屏幕，就必须重罚！
                        if (rect.width > winW * 0.9 && rect.height > winH * 0.9) {
                            ratioScore *= 0.0001; 
                        } else if (rect.width > winW * 0.8 && rect.height > winH * 0.8) {
                            // 对稍微小一点的整个右侧面板（可能包含了右侧浮动按钮和白底菜单栏）进行适度惩罚
                            ratioScore *= 0.01;
                        }
                        
                        // 如果元素的 left 非常小，说明它紧贴着左侧边缘，绝对包含了深色的左侧全局菜单栏，重罚！
                        if (rect.left < 10) {
                            ratioScore *= 0.001;
                        }

                        let score = area * ratioScore;
                        if (score > maxScore) {
                            maxScore = score;
                            bestEl = el;
                        }
                    }
                });
                window.__bestSlideEl = bestEl;
                return maxScore;
            }
            """
            
            target_el = None
            best_score = -1
            try:
                # 遍历所有 frame（包括主页面和 iframe），寻找最高得分的幻灯片容器
                for frame in active_page.frames:
                    try:
                        score = await frame.evaluate(js_find_slide_score)
                        if score and score > best_score:
                            best_score = score
                            # 获取挂载在 window 上的那个最佳元素
                            handle = await frame.evaluate_handle("window.__bestSlideEl")
                            if handle:
                                target_el = handle.as_element()
                    except Exception as fe:
                        pass
            except Exception as e:
                print(f"[调试] 定位目标元素时出错: {e}")

            # 第二步：基于找到的目标容器，提取网页 DOM 纯文本
            js_extract_text = """
            (element) => {
                function getText(node) {
                    if (node.nodeType === Node.ELEMENT_NODE) {
                        // 过滤掉不可见或不需要的标签
                        if (['SCRIPT', 'STYLE', 'SVG', 'CANVAS', 'NOSCRIPT'].includes(node.tagName.toUpperCase())) {
                            return '';
                        }
                        // 过滤隐藏元素
                        try {
                            let style = window.getComputedStyle(node);
                            if (style && (style.display === 'none' || style.visibility === 'hidden' || parseFloat(style.opacity) === 0)) {
                                return '';
                            }
                        } catch(e) {}
                        
                        let text = '';
                        let root = node.shadowRoot || node;
                        for (let child of root.childNodes) {
                            text += getText(child);
                        }
                        return text;
                    }
                    if (node.nodeType === Node.TEXT_NODE) {
                        let text = node.textContent.trim();
                        return text ? text + '\\n' : '';
                    }
                    return '';
                }
                return getText(element || document.body);
            }
            """
            
            body_text = ""
            html_dump = ""
            try:
                if target_el:
                    # 如果幻灯片是嵌套在 iframe 里的，深入 iframe 抓取文本
                    tag_name = await target_el.evaluate("el => el.tagName")
                    if tag_name.upper() == 'IFRAME':
                        frame = await target_el.content_frame()
                        if frame:
                            # 传入 frame 的 body 作为提取文本的起点
                            body_handle = await frame.evaluate_handle("document.body")
                            body_text = await frame.evaluate(js_extract_text, body_handle)
                            html_dump = await frame.content()
                    else:
                        body_text = await target_el.evaluate(js_extract_text)
                        html_dump = await target_el.evaluate("el => el.outerHTML")
                else:
                    body_text = await active_page.evaluate(js_extract_text)
                    html_dump = await active_page.content()
            except Exception as e:
                print(f"⚠️ 提取网页文本时出错: {e}")

            # debug文件使用"w"模式，每次都会覆盖写入当前页面的html，不会累加
            with open("debug_html.txt", "w", encoding="utf-8") as f:
                f.write(html_dump)
            
            cleaned_text = re.sub(r'\n\s*\n', '\n\n', body_text)

            # 第三步：对该精准容器进行截图
            try:
                if target_el:
                    await target_el.screenshot(path=screenshot_path)
                    print(f"📸 已精准抓拍幻灯片黑框区域，保存至: {screenshot_path}")
                else:
                    await active_page.screenshot(path=screenshot_path)
                    print(f"📸 未能定位到独立的幻灯片容器，已回退为全屏截图: {screenshot_path}")
            except Exception as e:
                target_el = None
                await active_page.screenshot(path=screenshot_path)
                print(f"📸 精准截图过程中发生异常 ({e})，已回退为全屏截图: {screenshot_path}")

            # ================= 新增 OCR 识别 =================
            ocr_text = ""
            if ocr_engine:
                print("正在进行本地图片 OCR 识别，请稍候...")
                try:
                    ocr_result, _ = ocr_engine(screenshot_path)
                    if ocr_result:
                        valid_texts = []
                        for item in ocr_result:
                            box = item[0]
                            text = item[1]
                            # box[0] 是左上角的坐标 [x, y]
                            x_left = box[0][0]
                            y_top = box[0][1]
                            
                            if target_el:
                                # 如果是精准截图（已裁剪黑框部分），保留所有文字
                                valid_texts.append((y_top, text))
                            else:
                                # 如果回退到了全屏截图，手动过滤掉侧边栏(x<280)和顶部栏(y<60)
                                if x_left > 280 and y_top > 60:
                                    valid_texts.append((y_top, text))
                        
                        # 根据 Y 坐标进行大致的从上到下排序
                        valid_texts.sort(key=lambda x: x[0])
                        ocr_text = "\n".join([t[1] for t in valid_texts])
                    
                    if ocr_text.strip():
                        print("✅ OCR 识别成功，已提取出整洁的题目文字！")
                except Exception as e:
                    print(f"⚠️ OCR 识别出错: {e}")

            # =================================================

            # 分别检查爬取文本和OCR文本是否重复
            crawled_duplicate = False
            if os.path.exists(crawled_output_file):
                with open(crawled_output_file, "r", encoding="utf-8") as f:
                    existing_content = f.read()
                    if cleaned_text.strip() and cleaned_text.strip() in existing_content:
                        crawled_duplicate = True

            ocr_duplicate = False
            if os.path.exists(ocr_output_file):
                with open(ocr_output_file, "r", encoding="utf-8") as f:
                    existing_content = f.read()
                    if ocr_text.strip() and ocr_text.strip() in existing_content:
                        ocr_duplicate = True

            if crawled_duplicate and (ocr_duplicate or not ocr_text.strip()):
                print("⚠️ 检测到内容已存在于文件中，跳过文本保存 (但已保存截图)。\n")
            else:
                final_header = f"\n\n\n=================== 第 {count} 次抓取 | 时间: {current_time} ===================\n"
                final_header += f"[对应截图: {screenshot_path}]\n\n"

                # 写入爬取的网页文本
                if cleaned_text.strip() and not crawled_duplicate:
                    with open(crawled_output_file, "a", encoding="utf-8") as f:
                        f.write(final_header + cleaned_text)
                    print("✅ 页面爬取文本保存成功！")
                elif cleaned_text.strip() and crawled_duplicate:
                    print("⚠️ 页面爬取文本重复，跳过保存。")

                # 写入 OCR 识别出的文本
                if ocr_text.strip() and not ocr_duplicate:
                    with open(ocr_output_file, "a", encoding="utf-8") as f:
                        f.write(final_header + ocr_text)
                    print("✅ OCR 识别文本保存成功！")
                elif ocr_text.strip() and ocr_duplicate:
                    print("⚠️ OCR 识别文本重复，跳过保存。")

                print(f"🎉 本次处理完成。你可以去浏览器切换下一题了！\n")

            count += 1

        print("\n抓取结束，正在关闭浏览器...")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(extract_yuketang_questions())

import json
import sys
from pathlib import Path #

def create_html_quiz_page(quiz_data): #
    """
    Generates a single HTML page string for an interactive quiz based on the provided quiz_data.
    """ #
    if not isinstance(quiz_data, dict): #
        raise ValueError("Quiz data must be a dictionary (keyed by exam number string)") #
    
    if not quiz_data: 
        raise ValueError("Quiz data dictionary is empty")

    try: #
        quiz_data_embedded_json = json.dumps(quiz_data, ensure_ascii=False, indent=None) 
    except (TypeError, ValueError) as e: #
        raise ValueError(f"Cannot serialize quiz data to JSON: {e}") #

    html_content = f"""<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>金融科技力知識檢定測驗 (完整版 - 隨機出題)</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 20px;
            background-color: #f4f4f4;
            color: #333;
            display: flex;
            flex-direction: column;
            align-items: center;
        }}
        
        #quiz-container {{
            background: #fff;
            padding: 25px;
            border-radius: 8px;
            box-shadow: 0 0 15px rgba(0,0,0,0.1);
            width: 100%;
            max-width: 800px;
        }}
        
        h1, h2, h3 {{
            color: #333;
            text-align: center;
        }}
        
        h1 {{
            font-size: 1.8em;
            margin-bottom: 15px;
        }}
        
        h2 {{
            font-size: 1.5em;
            margin-bottom: 10px;
        }}
        
        #exam-selection, #question-area, #results-area {{
            margin-top: 20px;
        }}
        
        #exam-selector {{
            display: block;
            width: 100%;
            padding: 12px;
            margin-bottom: 15px;
            border: 1px solid #ddd;
            border-radius: 4px;
            box-sizing: border-box;
            font-size: 1em;
        }}
        
        button {{
            display: block;
            width: 100%;
            padding: 12px 18px;
            background-color: #007bff;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 1.1em;
            transition: background-color 0.3s ease;
            margin-top: 10px;
        }}
        
        button:hover {{
            background-color: #0056b3;
        }}
        
        button:disabled {{
            background-color: #6c757d;
            cursor: not-allowed;
        }}
        
        #question-text {{
            margin-bottom: 18px;
            font-size: 1.1em;
            white-space: pre-wrap;
        }}
        
        .option {{
            background: #f9f9f9;
            border: 1px solid #eee;
            padding: 12px;
            margin-bottom: 10px;
            border-radius: 4px;
            cursor: pointer;
            transition: background-color 0.2s ease;
            font-size: 1em;
        }}
        
        .option:hover {{
            background: #e9e9e9;
        }}
        
        .option.selected {{
            background: #e7f3ff;
            border-color: #007bff;
        }}
        
        .option input[type="radio"] {{
            margin-right: 10px;
            vertical-align: middle;
        }}
        
        .option label {{
            vertical-align: middle;
            cursor: pointer;
            display: inline-block;
            width: calc(100% - 25px);
        }}
        
        #feedback {{
            color: #d9534f;
            font-weight: bold;
            margin-top: 10px;
            text-align: center;
        }}
        
        #progress-text {{
            text-align: center;
            margin-top: 15px;
            font-style: italic;
            color: #555;
        }}
        
        #score-text {{
            font-size: 1.3em;
            font-weight: bold;
            text-align: center;
            color: #007bff;
            margin-bottom: 20px;
        }}
        
        .review-item {{
            margin-bottom: 20px;
            padding: 15px;
            border: 1px solid #ddd;
            border-radius: 4px;
            background-color: #fdfdfd;
        }}
        
        .review-item p {{
            margin: 5px 0;
        }}
        
        .review-question {{
            font-weight: bold;
            white-space: pre-wrap;
        }}
        
        .user-answer.correct {{
            color: #5cb85c;
        }}
        
        .user-answer.incorrect {{
            color: #d9534f;
        }}
        
        .correct-answer-text {{
            color: #3c763d;
            font-weight: bold;
        }}
        
        .loading {{
            text-align: center;
            color: #666;
            font-style: italic;
        }}
        
        .error {{
            color: #d9534f;
            background-color: #f9f2f4;
            border: 1px solid #d1ecf1; 
            padding: 10px;
            border-radius: 4px;
            margin: 10px 0;
        }}
    </style>
</head>
<body>
    <div id="quiz-container">
        <h1>金融科技力知識檢定測驗 (完整版 - 隨機出題)</h1>
        
        <div id="exam-selection">
            <h2>請選擇測驗：</h2>
            <select id="exam-selector">
                <option value="">-- 選擇一個測驗 --</option>
            </select>
            <button id="start-quiz-btn">開始測驗</button>
        </div>

        <div id="question-area" style="display:none;">
            <h2 id="quiz-title"></h2>
            <p id="question-text"></p>
            <div id="options-container"></div>
            <p id="feedback" style="display:none;"></p>
            <button id="next-question-btn">下一題</button>
            <p id="progress-text"></p>
        </div>

        <div id="results-area" style="display:none;">
            <h2>測驗結果</h2>
            <p id="score-text"></p>
            <h3>題目回顧：</h3>
            <div id="review-area"></div>
            <button id="restart-quiz-btn">返回測驗選擇</button>
        </div>
    </div>

    <script>
        const rawQuizData = {quiz_data_embedded_json};
        let processedQuizData = {{ exams: [] }}; 

        // --- Data Transformation (same as before, includes point assignment) ---
        if (rawQuizData && typeof rawQuizData === 'object') {{
            processedQuizData.exams = Object.keys(rawQuizData).map(examKey => {{
                const originalExam = rawQuizData[examKey]; 
                const examNumber = originalExam.exam_number || parseInt(examKey);
                
                if (!originalExam.questions || !Array.isArray(originalExam.questions)) {{
                    console.error(`Exam "${{examKey}}" has no questions or questions are not an array.`);
                    return null; 
                }}

                return {{
                    exam_id: examKey,
                    title: `第 ${{examNumber}} 屆金融科技力知識檢定測驗`,
                    scoring_info: "第1-40題每題1.5分，第41-60題每題2分",
                    questions: originalExam.questions.map(q => {{
                        const questionNumber = q.question_number;
                        let points = 1.5; 
                        if (questionNumber >= 41 && questionNumber <= 60) {{ 
                            points = 2.0;
                        }}
                        
                        if (!q.options || typeof q.options !== 'object') {{
                             console.error(`Question ${{questionNumber}} in exam "${{examKey}}" has invalid options.`);
                             return {{ 
                                id: questionNumber,
                                text: q.question_text || "題目文字遺失",
                                options: [],
                                answer: parseInt(q.answer) || 0, 
                                points: points
                             }};
                        }}

                        return {{
                            id: questionNumber,
                            text: q.question_text || "題目文字遺失",
                            options: Object.keys(q.options).map(optKey => ({{
                                option_id: parseInt(optKey),
                                text: q.options[optKey]
                            }})),
                            answer: parseInt(q.answer), 
                            points: points 
                        }};
                    }}).filter(q => q && q.options && q.options.length > 0), 
                    answer_sheet_source_id: `Exam ${{examKey}} data`
                }};
            }}).filter(exam => exam !== null && exam.questions && exam.questions.length > 0); 
        }}
        // --- End Data Transformation ---
        
        let currentExamData = null;
        let currentQuestionIndex = 0;
        let userAnswers = [];
        let totalScore = 0;

        const examSelector = document.getElementById('exam-selector');
        const startQuizBtn = document.getElementById('start-quiz-btn');
        const examSelectionDiv = document.getElementById('exam-selection');
        const questionAreaDiv = document.getElementById('question-area');
        const resultsAreaDiv = document.getElementById('results-area');
        const quizTitleEl = document.getElementById('quiz-title');
        const questionTextEl = document.getElementById('question-text');
        const optionsContainerEl = document.getElementById('options-container');
        const feedbackEl = document.getElementById('feedback');
        const nextQuestionBtn = document.getElementById('next-question-btn');
        const progressTextEl = document.getElementById('progress-text');
        const scoreTextEl = document.getElementById('score-text');
        const reviewAreaEl = document.getElementById('review-area');
        const restartQuizBtn = document.getElementById('restart-quiz-btn');
        
        function showError(message) {{ 
            console.error(message); 
            const errorDivOld = document.querySelector('.error');
            if(errorDivOld) errorDivOld.remove(); 
            const errorDiv = document.createElement('div'); 
            errorDiv.className = 'error'; 
            errorDiv.textContent = message; 
            const container = document.getElementById('quiz-container'); 
            if (container) {{ 
                 container.insertBefore(errorDiv, container.firstChild); 
            }}
        }}

        function hideError() {{ 
            const errorDiv = document.querySelector('.error'); 
            if (errorDiv) {{ 
                errorDiv.remove(); 
            }}
        }}

        function validateProcessedQuizData() {{ 
            if (!processedQuizData || typeof processedQuizData !== 'object') {{ 
                throw new Error('無效的已處理測驗資料格式'); 
            }}
            
            if (!processedQuizData.exams || !Array.isArray(processedQuizData.exams)) {{ 
                throw new Error('已處理測驗資料中缺少有效的測驗列表'); 
            }}
            
            if (processedQuizData.exams.length === 0) {{ 
                const rawExamCount = rawQuizData ? Object.keys(rawQuizData).length : 0;
                if (rawExamCount > 0) {{
                    throw new Error('所有原始測驗資料轉換後均無效或沒有題目。請檢查 quiz_data.json 的內容與結構。');
                }} else {{
                    throw new Error('沒有可用的測驗'); 
                }}
            }}
            
            processedQuizData.exams.forEach((exam, examIndex) => {{ 
                if (!exam.title || typeof exam.title !== 'string') {{ 
                    throw new Error(`測驗索引 ${{examIndex}} 缺少有效的標題`); 
                }}
                if (!exam.questions || !Array.isArray(exam.questions) || exam.questions.length === 0) {{ 
                     throw new Error(`測驗 "${{exam.title}}" 沒有題目或題目列表無效`);
                }}
                exam.questions.forEach((question, questionIndex) => {{ 
                    if (typeof question.id === 'undefined' || typeof question.text !== 'string') {{ 
                        throw new Error(`測驗 "${{exam.title}}" 第 ${{questionIndex + 1}} 題缺少必要資訊 (ID or text)`); 
                    }}
                    if (!question.options || !Array.isArray(question.options) || question.options.length === 0) {{ 
                        throw new Error(`測驗 "${{exam.title}}" 第 ${{questionIndex + 1}} 題缺少選項`); 
                    }}
                    if (typeof question.points !== 'number' || question.points <= 0) {{ 
                        throw new Error(`測驗 "${{exam.title}}" 第 ${{questionIndex + 1}} 題分數無效 (得到: ${{question.points}})`); 
                    }}
                    if (typeof question.answer !== 'number') {{ 
                        throw new Error(`測驗 "${{exam.title}}" 第 ${{questionIndex + 1}} 題缺少正確答案(或非數字格式)`); 
                    }}
                    const answerExists = question.options.some(opt => opt.option_id === question.answer); 
                    if (!answerExists) {{ 
                        throw new Error(`測驗 "${{exam.title}}" 第 ${{questionIndex + 1}} 題的正確答案 (${{question.answer}}) 不在選項中`); 
                    }}
                }});
            }});
        }}

        // Fisher-Yates (Knuth) Shuffle function
        function shuffleArray(array) {{
            for (let i = array.length - 1; i > 0; i--) {{
                const j = Math.floor(Math.random() * (i + 1));
                [array[i], array[j]] = [array[j], array[i]]; // Swap elements
            }}
        }}

        function populateExamSelector() {{ 
            try {{ 
                hideError(); 
                validateProcessedQuizData(); 
                examSelector.innerHTML = '<option value="">-- 選擇一個測驗 --</option>'; 
                processedQuizData.exams.forEach((exam, index) => {{ 
                    const optionElement = document.createElement('option'); 
                    optionElement.value = index; 
                    optionElement.textContent = `${{exam.title}} (${{exam.questions.length}} 題)`; 
                    examSelector.appendChild(optionElement); 
                }});
                startQuizBtn.disabled = false; 
            }} catch (error) {{ 
                showError(`載入測驗資料時發生錯誤：${{error.message}}`); 
                startQuizBtn.disabled = true; 
            }}
        }}

        function startQuiz() {{ 
            try {{ 
                const selectedExamIndex = examSelector.value; 
                if (selectedExamIndex === "") {{ 
                    showError("請先選擇一個測驗！"); 
                    return; 
                }}

                hideError(); 
                // Create a deep copy of the selected exam's data to shuffle
                // This prevents modifying the original processedQuizData structure if the user re-selects the same exam
                let selectedExamObject = JSON.parse(JSON.stringify(processedQuizData.exams[parseInt(selectedExamIndex)]));
                
                // Shuffle the questions array of the copied exam data
                if (selectedExamObject.questions && selectedExamObject.questions.length > 0) {{
                    shuffleArray(selectedExamObject.questions);
                }}
                currentExamData = selectedExamObject; // Use the exam with shuffled questions

                currentQuestionIndex = 0; 
                userAnswers = new Array(currentExamData.questions.length).fill(null); 
                totalScore = 0; 

                quizTitleEl.textContent = currentExamData.title; 
                examSelectionDiv.style.display = 'none'; 
                resultsAreaDiv.style.display = 'none'; 
                questionAreaDiv.style.display = 'block'; 
                
                displayQuestion(); 
            }} catch (error) {{ 
                showError(`開始測驗時發生錯誤：${{error.message}}`); 
            }}
        }}

        function displayQuestion() {{ 
            try {{ 
                if (!currentExamData || currentQuestionIndex >= currentExamData.questions.length) {{ 
                    showResults(); 
                    return; 
                }}

                const question = currentExamData.questions[currentQuestionIndex]; 
                questionTextEl.textContent = `${{question.id}}. ${{question.text}} (${{question.points.toFixed(1)}}分)`; 
                optionsContainerEl.innerHTML = ''; 
                feedbackEl.style.display = 'none'; 

                question.options.forEach(opt => {{ 
                    const div = document.createElement('div'); 
                    div.classList.add('option'); 
                    
                    const radio = document.createElement('input'); 
                    radio.type = 'radio'; 
                    radio.name = 'question_option'; 
                    radio.value = opt.option_id; 
                    radio.id = `q${{currentQuestionIndex}}_opt${{opt.option_id}}`; 

                    const label = document.createElement('label'); 
                    label.htmlFor = radio.id; 
                    label.textContent = `(${{opt.option_id}}) ${{opt.text}}`; 
                    
                    div.appendChild(radio); 
                    div.appendChild(label); 
                    
                    div.addEventListener('click', function() {{ 
                        radio.checked = true; 
                        document.querySelectorAll('.option').forEach(el => el.classList.remove('selected')); 
                        div.classList.add('selected'); 
                    }});
                    
                    radio.addEventListener('change', function() {{ 
                        document.querySelectorAll('.option').forEach(el => el.classList.remove('selected')); 
                        div.classList.add('selected'); 
                    }});
                    
                    optionsContainerEl.appendChild(div); 
                }});

                progressTextEl.textContent = `第 ${{currentQuestionIndex + 1}} / ${{currentExamData.questions.length}} 題`; 
                nextQuestionBtn.textContent = (currentQuestionIndex === currentExamData.questions.length - 1) ? "提交測驗" : "下一題"; 
            }} catch (error) {{ 
                showError(`顯示題目時發生錯誤：${{error.message}}`); 
            }}
        }}

        function processNextQuestion() {{ 
            try {{ 
                const selectedOption = optionsContainerEl.querySelector('input[name="question_option"]:checked'); 
                if (!selectedOption) {{ 
                    feedbackEl.textContent = "請選擇一個答案！"; 
                    feedbackEl.style.display = 'block'; 
                    return; 
                }}
                
                userAnswers[currentQuestionIndex] = parseInt(selectedOption.value); 
                feedbackEl.style.display = 'none'; 
                currentQuestionIndex++; 
                
                if (currentQuestionIndex < currentExamData.questions.length) {{ 
                    displayQuestion(); 
                }} else {{ 
                    showResults(); 
                }}
            }} catch (error) {{ 
                showError(`處理答案時發生錯誤：${{error.message}}`); 
            }}
        }}

        function showResults() {{ 
            try {{ 
                questionAreaDiv.style.display = 'none'; 
                resultsAreaDiv.style.display = 'block'; 
                reviewAreaEl.innerHTML = ''; 
                totalScore = 0; 

                let maxScore = 0; 
                currentExamData.questions.forEach((question, index) => {{ 
                    maxScore += question.points; 
                    
                    const userAnswerId = userAnswers[index]; 
                    const correctAnswerId = question.answer; 
                    const isCorrect = userAnswerId === correctAnswerId; 
                    const pointsEarned = isCorrect ? question.points : 0; 
                    totalScore += pointsEarned; 

                    const reviewItem = document.createElement('div'); 
                    reviewItem.classList.add('review-item'); 
                    
                    const questionTextElement = document.createElement('p'); 
                    questionTextElement.classList.add('review-question'); 
                    questionTextElement.textContent = `${{question.id}}. ${{question.text}} (${{question.points.toFixed(1)}}分)`; 
                    reviewItem.appendChild(questionTextElement); 

                    const userAnswerObj = question.options.find(opt => opt.option_id === userAnswerId); 
                    const userAnswerParagraph = document.createElement('p'); 
                    const answerClass = isCorrect ? 'correct' : 'incorrect'; 
                    const answerDisplayText = userAnswerObj ? `(${{userAnswerObj.option_id}}) ${{userAnswerObj.text}}` : '未作答'; 
                    userAnswerParagraph.innerHTML = `您的答案：<span class="user-answer ${{answerClass}}">${{answerDisplayText}}</span>`; 
                    reviewItem.appendChild(userAnswerParagraph); 

                    if (!isCorrect) {{ 
                        const correctAnswerObj = question.options.find(opt => opt.option_id === correctAnswerId); 
                        const correctAnswerParagraph = document.createElement('p'); 
                        const correctDisplayText = correctAnswerObj ? `(${{correctAnswerObj.option_id}}) ${{correctAnswerObj.text}}` : 'N/A'; 
                        correctAnswerParagraph.innerHTML = `正確答案：<span class="correct-answer-text">${{correctDisplayText}}</span>`; 
                        reviewItem.appendChild(correctAnswerParagraph); 
                    }}
                    
                    const pointsParagraph = document.createElement('p'); 
                    pointsParagraph.textContent = `本題得分：${{pointsEarned.toFixed(1)}} / ${{question.points.toFixed(1)}} 分`; 
                    reviewItem.appendChild(pointsParagraph); 

                    reviewAreaEl.appendChild(reviewItem); 
                }});
                
                const percentage = maxScore > 0 ? ((totalScore / maxScore) * 100).toFixed(1) : 0; 
                scoreTextEl.textContent = `您的總得分：${{totalScore.toFixed(1)}} / ${{maxScore.toFixed(1)}} 分 (${{percentage}}%)`; 
            }} catch (error) {{ 
                showError(`顯示結果時發生錯誤：${{error.message}}`); 
            }}
        }}
        
        function restartQuiz() {{ 
            try {{ 
                hideError(); 
                resultsAreaDiv.style.display = 'none'; 
                questionAreaDiv.style.display = 'none'; 
                examSelectionDiv.style.display = 'block'; 
                examSelector.value = ""; 
                
                currentExamData = null; 
                currentQuestionIndex = 0; 
                userAnswers = []; 
                totalScore = 0; 
            }} catch (error) {{ 
                showError(`重置測驗時發生錯誤：${{error.message}}`); 
            }}
        }}

        document.addEventListener('DOMContentLoaded', function() {{ 
            try {{ 
                populateExamSelector(); 
            }} catch (error) {{ 
                showError(`初始化應用程式時發生錯誤：${{error.message}}`); 
            }}
        }});
        
        startQuizBtn.addEventListener('click', startQuiz); 
        nextQuestionBtn.addEventListener('click', processNextQuestion); 
        restartQuizBtn.addEventListener('click', restartQuiz); 

        document.addEventListener('keydown', function(event) {{ 
            if (questionAreaDiv.style.display !== 'none') {{ 
                if (event.key >= '1' && event.key <= '9') {{ 
                    const optionIndex = parseInt(event.key) - 1; 
                    const options = optionsContainerEl.querySelectorAll('input[type="radio"]'); 
                    if (options[optionIndex]) {{ 
                        options[optionIndex].checked = true; 
                        options[optionIndex].dispatchEvent(new Event('change')); 
                    }}
                }}
                else if (event.key === 'Enter' || event.key === ' ') {{ 
                    event.preventDefault(); 
                    processNextQuestion(); 
                }}
            }}
        }});

    </script>
</body>
</html>""" #
    
    return html_content #

def main(): #
    """Main function to handle file operations and error reporting.""" #
    try: #
        quiz_file = Path('quiz_data.json') #
        
        if not quiz_file.exists(): #
            raise FileNotFoundError(f"找不到測驗資料檔案：{quiz_file}") #
        
        with quiz_file.open('r', encoding='utf-8') as f: #
            quiz_data = json.load(f) #
        
        html_output = create_html_quiz_page(quiz_data) #
        
        if hasattr(sys.stdout, 'reconfigure'): #
            sys.stdout.reconfigure(encoding='utf-8') #
        
        print(html_output) #
        
    except FileNotFoundError as e: #
        error_message = ( #
            f"錯誤：{str(e)}\n"
            "請確認您已將JSON測驗資料儲存為 'quiz_data.json'，\n"
            "並且該檔案與此Python程式位於同一個資料夾中。"
        )
        print(error_message, file=sys.stderr) #
        sys.exit(1) #
        
    except json.JSONDecodeError as e: #
        error_message = ( #
            f"錯誤：無法解析 'quiz_data.json' 檔案。\n"
            f"JSON 格式錯誤：{str(e)}\n"
            "請確認該檔案包含有效的JSON格式資料且為UTF-8編碼。"
        )
        print(error_message, file=sys.stderr) #
        sys.exit(1) #
        
    except ValueError as e: #
        error_message = f"資料驗證或處理錯誤：{str(e)}" #
        print(error_message, file=sys.stderr) #
        sys.exit(1) #
        
    except Exception as e: #
        error_message = f"發生未預期的錯誤：{str(e)}" #
        print(error_message, file=sys.stderr) #
        sys.exit(1) #

if __name__ == '__main__': #
    main() #
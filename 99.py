import random

def multiplication_quiz():
    correct_count = 0  # 初始化正確答題計數器
    
    while correct_count < 10:  # 當正確答題計數器小於 10 時持續出題
        # 隨機選擇兩個數字作為題目
        num1 = random.randint(1, 9)
        num2 = random.randint(1, 9)
        
        # 計算正確答案
        correct_answer = num1 * num2
        
        while True:  # 使用內部迴圈處理輸入錯誤的情況
            try:
                # 提示題目並讀取使用者的回答
                user_answer = int(input(f"{num1} * {num2}是多少? "))
                
                # 檢查答案是否正確
                if user_answer == correct_answer:
                    print("恭喜你答對了!")
                    correct_count += 1  # 正確答題計數器加一
                    print(f"已經答對了 {correct_count} 題！\n")
                    break  # 跳出內部迴圈，出下一題
                else:
                    print("嗯...再多想想答案吧\n")
                    
            except ValueError:
                print("請輸入有效的數字!")
    
    # 當答對十題時，顯示鼓勵訊息
    print("恭喜你成功答對十題，做得很好！")
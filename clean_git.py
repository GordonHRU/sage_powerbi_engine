import os
import subprocess

def run_command(command):
    print(f"執行: {command}")
    subprocess.run(command, shell=True, check=True)

def main():
    print("開始清理 Git 追蹤...")
    
    # 拉取最新變更
    run_command("git pull")
    
    # 清理 Git 追蹤
    run_command("git rm -r --cached .")
    
    # 重新添加檔案
    run_command("git add .")
    
    # 提交變更
    run_command('git commit -m "Remove .pyc files from git tracking"')
    
    # 推送到遠端
    run_command("git push")
    
    print("清理完成！")

if __name__ == "__main__":
    main() 
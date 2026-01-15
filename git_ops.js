
const fs = require('fs');
const path = require('path');
const git = require('isomorphic-git');

const REMOTE_URL = 'https://github.com/jnnni1220-dev/project2-1.git';

async function runGit() {
    const dir = process.cwd();

    console.log('--- Git 초기화 시작 ---');
    try {
        await git.init({ fs, dir });
        console.log('Git 저장소가 초기화되었습니다.');

        // 파일 목록 가져오기 (재귀적)
        function getAllFiles(dirPath, arrayOfFiles) {
            const files = fs.readdirSync(dirPath);
            arrayOfFiles = arrayOfFiles || [];

            files.forEach(function (file) {
                if (fs.statSync(dirPath + "/" + file).isDirectory()) {
                    if (file !== '.git' && file !== 'node_modules' && file !== 'models' && file !== 'Dunnhumby') {
                        arrayOfFiles = getAllFiles(dirPath + "/" + file, arrayOfFiles);
                    }
                } else {
                    const relativePath = path.relative(process.cwd(), path.join(dirPath, "/", file)).replace(/\\/g, '/');
                    // .gitignore에 정의된 확장자 제외 (간이 구현)
                    if (!['.csv', '.zip', '.msi', '.xlsx', '.png', '.jpg'].some(ext => relativePath.toLowerCase().endsWith(ext))) {
                        arrayOfFiles.push(relativePath);
                    } else if (relativePath.includes('final_reports') && (relativePath.endsWith('.png') || relativePath.endsWith('.jpg'))) {
                        // 보고서 내 이미지는 포함
                        arrayOfFiles.push(relativePath);
                    }
                }
            });
            return arrayOfFiles;
        }

        const filesToAdd = getAllFiles(dir);
        console.log(`추가할 파일 수: ${filesToAdd.length}`);

        for (const filepath of filesToAdd) {
            await git.add({ fs, dir, filepath });
        }
        console.log('모든 파일이 스테이징되었습니다.');

        const sha = await git.commit({
            fs,
            dir,
            author: {
                name: 'Antigravity AI',
                email: 'antigravity@google.com'
            },
            message: 'Dunnhumby 분석 고도화 및 보고서 개편 최종 완료'
        });
        console.log(`커밋 완료! (SHA: ${sha})`);

        console.log('--- 원격 저장소 설정 ---');
        await git.addRemote({
            fs,
            dir,
            remote: 'origin',
            url: REMOTE_URL
        });
        console.log(`원격 저장소(origin)가 설정되었습니다: ${REMOTE_URL}`);

    } catch (err) {
        console.error('Git 작업 중 오류 발생:', err);
    }
}

runGit();

# Gemini (`ego-browser v2.2.1`) 이미지 생성 플레이북

> **핵심 환경 제약**: `ego-browser nodejs`는 셸의 작업 폴더(`cwd`)와 `process.env`를 상속하지 않는다. 모든 저장 경로는 반드시 `<PROJECT_ROOT>/...` 절대경로를 사용한다.

## 1. 타깃 창 & 고정 옵션
- **URL**: `https://gemini.google.com/app/<YOUR_CHAT_ID>` (사이드바 제목: `SNS용 웹툰 이미지 생성`)
- **고정 설정**: 비율 **`3:4`** · 형식 **`이미지`** · 모델 **`Hydrogen`**

## 2. 페이지 진입 및 상태 스냅샷 템플릿
```bash
ego-browser nodejs <<'EOF'
const SPACE_ID = null; // state.json에 기존 id가 있으면 숫자 대입
const entry = SPACE_ID === null ? undefined : (await listTaskSpaces()).find((s) => s.id === SPACE_ID);
const task = !entry
  ? await taskSpace("ai-news-studio")
  : entry.ownership === "user"
    ? await claimTaskSpace(SPACE_ID)
    : entry.ownership === "agentDelegatedToUser"
      ? await takeOverTaskSpace(SPACE_ID)
      : await taskSpace(SPACE_ID);

const page = (await task.pages())[0] ?? (await task.adopt((await task.tabs())[0].page));
await page.goto("https://gemini.google.com/app/<YOUR_CHAT_ID>");
await page.waitForLoadState();
console.log({ taskSpaceId: task.spaceId, page: page.label, url: page.url() });
console.log(await page.snapshot());
EOF
```

## 3. 로그인 체크 & `handOff()`
- 스냅샷에 `로그인` / `Sign in` 버튼이 보이거나 Google 로그인 페이지로 리다이렉트되면 **절대 우회하지 않고**:
  ```js
  await task.handOff();
  ```
  호출 후 `director`에게 *"에고라이트 Gemini 창에서 구글 로그인 후 '완료'라고 답해주세요"*를 보고한다.

## 4. 옵션(`3:4` · `이미지` · `Hydrogen`) 확인 & 프롬프트 입력 (실측 셀렉터)
1. 첫 진입 시 하단에 `이미지` 칩이 비활성일 수 있다:
   - `button[aria-label="업로드 및 도구"]` 클릭 → `menuitemcheckbox` `"이미지 만들기"` 클릭.
   - `button[aria-label="모드 선택 도구 열기..."]`가 **`Hydrogen`**인지 확인.
   - `"가로세로 비율"` 버튼 클릭 → `menuitemradio "3:4"` 선택.
   - `"형식"` 버튼 클릭 → `menuitemradio "이미지"` 선택.
2. 입력창(`textfield "Gemini 프롬프트 입력"`) 클릭 → `await page.keyboard.paste(promptText)` → `await page.keyboard.press("Enter")`.

## 5. 이미지 생성 완료 감지 & 저장 (실측 주의사항)
- **주의**: Gemini는 이미지 생성 완료 후에도 숨은 DOM 텍스트에 `"Creating your image"`가 남을 수 있으므로 텍스트 부재로 대기하지 않는다. 대신 **생성 전 기존 `blob:` 이미지 개수/다운로드 버튼 수를 저장**한 뒤 증가를 감지한다:
  ```js
  await page.waitForFunction(
    (prev) => {
      const dlBtns = document.querySelectorAll('button[aria-label="원본 크기 이미지 다운로드"]');
      const blobs = [...document.querySelectorAll("img")].filter(
        (i) => i.src.startsWith("blob:") && i.naturalWidth >= 400
      );
      return dlBtns.length > prev.dlCount && blobs.length > prev.blobCount;
    },
    prev,
    { timeout: 120_000 }
  );
  ```
- **다운로드/추출**:
  - 하단 입력창(`<input-companion-chip>`)이 이미지 hover/클릭을 가릴 수 있다. 우선 `<canvas>`에 최신 `blob:` 이미지를 그려 `toDataURL("image/png")`로 원본 해상도(`896×1200`)를 `fs.writeFile`로 저장하는 방식이 오버레이 간섭 없이 가장 안정적이다.
- 저장 직후 `Read`로 PNG 파일을 직접 열어 한글 깨짐·잘림·3:4 비율을 시각 검수한다.

<template>
  <div class="chatgit-logo">
    <svg viewBox="0 0 240 80" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <linearGradient id="textGradient" x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%" stop-color="#3b82f6" />
          <stop offset="100%" stop-color="#9333ea" />
        </linearGradient>
      </defs>
      <text
        x="50%"
        y="60%"
        dominant-baseline="middle"
        text-anchor="middle"
        font-family="Fira Code, Monaco, Consolas, monospace"
        font-weight="bold"
        font-size="40"
        fill="url(#textGradient)"
      >
        ChatGit
      </text>
    </svg>
  </div>
</template>

<style scoped>
/* 通过修改容器class控制SVG大小 */
.chatgit-logo {
  width: 240px; /* 默认大小 */
  height: 80px;
}

/* 使用示例 */
.chatgit-logo.small {
  width: 120px;
  height: 40px;
}

.chatgit-logo.large {
  width: 360px;
  height: 120px;
}

/* 保持SVG自适应容器 */
.chatgit-logo svg {
  width: 100%;
  height: 100%;
}
</style>

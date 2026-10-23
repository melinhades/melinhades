<div align="center">
<img src="./assets/banner.svg" alt="Mount Celeste · pixel night" width="100%" />

<img src="https://readme-typing-svg.demolab.com?font=Press+Start+2P&size=18&pause=1600&color=9B87F5&background=00000000&center=true&vCenter=true&width=840&height=72&lines=Software+engineering+student+%40+TYUT;Full-stack%3A+Spring+Boot+%2B+vanilla+JS+%2B+AI;Ten+kilometers+before+sunrise%2C+every+day.;Fall+a+thousand+times%2C+press+retry+a+thousand+times." alt="typing" />

<img src="https://img.shields.io/badge/TYUT-Software%20Engineering%20%C2%B7%20Junior-9B87F5?style=for-the-badge" alt="TYUT" />
<img src="https://img.shields.io/badge/Celeste-Peak%20cleared-FF6B9D?style=for-the-badge" alt="Celeste" />
</div>

## Who I Am

Junior software engineering student at Taiyuan University of Technology.

Two things define how I work: a 10km run before sunrise every day, and Celeste — a pixel game about climbing a mountain. One trains discipline, the other shaped how I deal with difficulty: **falling isn't failure; stopping is.**

This page is not a résumé. It's a record of a path still being walked — from vanilla JavaScript to Spring Boot, from calling libraries to implementing them, from a diary app to an AI system under continuous iteration.

<div align="center"><img src="./assets/divider.svg" width="100%" /></div>

## How I Think About Engineering

**From Celeste:** the voice saying "you can't" isn't defeated — it's carried up the mountain with you. Translated to engineering: bugs aren't enemies to eliminate, they're signals to understand. A level can kill you a thousand times; attempt one thousand and one still works.

**From running:** there's no shortcut and no audience for 10km. What separates people isn't the required work — it's whether you still do the things nobody asked for. A compile error at midnight and a 5am alarm are the same kind of moment.

<img src="./assets/dawn.svg" width="100%" />

The direct product of this mindset is the project below.

<div align="center"><img src="./assets/divider.svg" width="100%" /></div>

## Work

### [Celeste-AI-Diary-Companion-Blog](https://github.com/melinhades/Celeste-AI-Diary-Companion-Blog)

A full-stack blog with an AI diary companion, under active iteration. The stack is deliberately unfashionable — every layer is hand-built and understood:

| Layer | Implementation | Key decisions |
| :--- | :--- | :--- |
| Backend | Spring Boot 2.5 + MyBatis-Plus + MySQL | No Spring AI — conversation memory, emotion extraction, and persona validation are hand-written |
| Frontend | Vanilla HTML/JS, zero frameworks | SSE stream parsing, typing-trajectory collection, debounced interruption — all implemented from scratch |
| AI pipeline | RAG retrieval (vector cache + time decay + importance fusion + per-source quotas), dual-modal emotion analysis (text × typing dynamics), persona red-line checker | State machine and persona rules documented before any code |
| Verifiability | Full-chain logging (trigger → retrieval → emotion → generation → feedback), LLM-as-Judge, ablation tests, 👍👎 loop | "It feels better" is not accepted — only measurable deltas |

The question it answers: **how does an AI companion stay warm without fabricating, real-time yet interruptible, and memorable without decaying?** Current focus: retrieval-depth iteration.

<div align="center"><img src="./assets/divider.svg" width="100%" /></div>

## Growth Trajectory

**Currently learning (beyond coursework):**

| Area | Approach | Status |
| :--- | :--- | :--- |
| Machine learning | Implementing from scratch in NumPy, no libraries | In progress |
| Frontend | Vanilla first, frameworks later | Ongoing |
| LLM applications | The diary project above as the testbed | Iterating |
| Running | 10km daily | Daily habit |

**Consistency, made visible (running can't be screenshotted — commits can):**

<img src="https://streak-stats.demolab.com?user=melinhades&theme=transparent&hide_border=true&ring=9B87F5&fire=FF6B9D&currStreakLabel=9B87F5&sideLabels=9B87F5&currStreakNum=9B87F5&sideNums=9B87F5&dates=8b949e" alt="streak" />

**Next:**

- Turn the from-scratch ML work into a runnable set of notes
- Go deeper on the diary project: retrieval, memory, verification — one module at a time
- Keep the streak boring

<div align="center"><img src="./assets/divider.svg" width="100%" /></div>

## Contact

Happy to talk about Celeste's level design, framework-free frontend, RAG engineering, or running.

📮 [jfy2846484252@outlook.com](mailto:jfy2846484252@outlook.com)

<div align="center"><img src="./assets/divider.svg" width="100%" /></div>

<div align="center">
*The mountain is right there. Just climb.*
</div>

<!--
贪吃蛇贡献图：等 .github/workflows/snake.yml 第一次跑成功再启用。
首次跑之前这个链是 404，会显示破图，所以先注释着。
想启用就把下面这段的注释去掉。

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/melinhades/melinhades/output/snake-dark.svg" />
    <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/melinhades/melinhades/output/snake.svg" />
    <img alt="contribution snake" src="https://raw.githubusercontent.com/melinhades/melinhades/output/snake.svg" />
  </picture>
</p>
-->

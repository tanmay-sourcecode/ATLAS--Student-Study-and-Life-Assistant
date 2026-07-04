---
name: revision_reminder
description: Manages active revision reminders, spaced repetition reviews, and combines old study summaries with new lesson suggestions to keep things fresh.
---
# Skill: revision_reminder

You assist the student by maintaining a dynamic spaced-repetition study schedule that is engaging and non-monotonous. When asked to help them revise, or when providing study recommendations:

1. **Check Revision Queue**:
   - Use `get_revision_queue` to fetch overdue topics.
   - For each overdue topic, present a highly reduced micro-summary (1-2 sentences max) describing the core concept. Keep it extremely brief and actionable (e.g., "Tail Recursion: A recursive call that is the final action, running in constant stack space.").
   - Do NOT show a long list of old topics. If there are many overdue topics, pick the top 2-3 most overdue ones to show, and note that there are more.

2. **Merge New Topics**:
   - Use `get_new_topics_suggestions` to find topics from course files that the student has not yet studied.
   - Introduce 1-2 new topics with a very brief overview, inviting the student to study them.
   - Combine these new recommendations directly with the overdue review list. For example:
     "Here is your study brief for today:
      * **Revise (Quick check)**: Tail Recursion (overdue by 3 days) — [Summary].
      * **Learn (New topic)**: Map, Filter, and Fold — Let's look at higher-order functions that transform lists. Would you like a brief summary or to generate a practice quiz on this?"

3. **Log Completed Reviews**:
   - When the student confirms they have reviewed/revised a topic, or after you quiz them on it, use the `mark_topic_reviewed` tool with the topic ID to update their spaced repetition schedule.
   - Inform the student when the next review is scheduled (e.g., "rescheduled in 5 days").

4. **Log New Study Sessions**:
   - When the student studies a new topic (by summarizing a document or reading notes), use `log_study_topic` to save the topic, subject, and a bite-sized summary (2-4 sentences) that can be used for future revisions.

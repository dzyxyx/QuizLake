import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import MyQuizCard from '@/components/MyQuizCard.vue'
import type { Quiz } from '@/types'

function makeQuiz(overrides: Partial<Quiz> = {}): Quiz {
  return {
    id: 1,
    owner_id: 1,
    category_id: null,
    title: 'My Quiz',
    description: null,
    difficulty: 'easy',
    time_per_question_sec: 20,
    speed_bonus_enabled: true,
    show_correct_answer: true,
    allow_answer_change: false,
    is_public: false,
    status: 'draft',
    cover_image_url: null,
    ...overrides,
  }
}

describe('MyQuizCard', () => {
  it('renders the title and status label for a draft quiz', () => {
    const wrapper = mount(MyQuizCard, { props: { quiz: makeQuiz({ status: 'draft' }) } })

    expect(wrapper.text()).toContain('My Quiz')
    expect(wrapper.text()).toContain('Черновик')
    expect(wrapper.text()).toContain('Опубликовать')
    expect(wrapper.text()).not.toContain('Запустить')
  })

  it('shows a launch button instead of publish once the quiz is ready', () => {
    const wrapper = mount(MyQuizCard, { props: { quiz: makeQuiz({ status: 'ready' }) } })

    expect(wrapper.text()).toContain('Запустить')
    expect(wrapper.text()).not.toContain('Опубликовать')
  })

  it('shows neither publish nor launch for an archived quiz', () => {
    const wrapper = mount(MyQuizCard, { props: { quiz: makeQuiz({ status: 'archived' }) } })

    expect(wrapper.text()).not.toContain('Опубликовать')
    expect(wrapper.text()).not.toContain('Запустить')
  })

  it('emits edit with the quiz id when the edit button is clicked', async () => {
    const wrapper = mount(MyQuizCard, { props: { quiz: makeQuiz({ id: 42 }) } })

    await wrapper.find('.btn-secondary').trigger('click')

    expect(wrapper.emitted('edit')).toEqual([[42]])
  })

  it('emits publish with the quiz id when publish is clicked on a draft quiz', async () => {
    const wrapper = mount(MyQuizCard, { props: { quiz: makeQuiz({ id: 42, status: 'draft' }) } })

    await wrapper.find('.btn-primary').trigger('click')

    expect(wrapper.emitted('publish')).toEqual([[42]])
  })

  it('emits launch with the quiz id when launch is clicked on a ready quiz', async () => {
    const wrapper = mount(MyQuizCard, { props: { quiz: makeQuiz({ id: 42, status: 'ready' }) } })

    await wrapper.find('.btn-primary').trigger('click')

    expect(wrapper.emitted('launch')).toEqual([[42]])
  })
})

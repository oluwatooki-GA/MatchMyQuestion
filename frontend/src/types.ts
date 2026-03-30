export interface Question {
  question: string
  options: string[] | null
  correct_answer: string | null
  correct_answer_letter: string | null
  explanation_html: string | null
  subject: string
  exam_type: string
  year: string
  image_url: string | null
}

export interface SubjectSection {
  title: string
  subjects: Record<string, string[]>
}

export interface SelectedSubjectsState {
  [key: string]: Record<string, string[]>
}

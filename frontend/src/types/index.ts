// Types
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

export interface SubjectYear {
  subject: string
  years: string[]
}

export interface SearchRequest {
  q: string
  search_items: SubjectYear[]
}

export interface SearchResult {
  result: Question[] | null
}

export interface SelectedSubjectsState {
  [key: string]: Record<string, string[]>
}

import { useState } from 'react'
import { searchQuestions } from '../lib/api'
import type { Question, SelectedSubjectsState, SubjectYear } from '../types'

export function useSearchForm() {
  const [input, setInput] = useState('')
  const [selectedSubjects, setSelectedSubjects] = useState<SelectedSubjectsState>({})
  const [questions, setQuestions] = useState<Question[]>([])
  const [isLoading, setIsLoading] = useState(false)

  const handleYearChange = (sectionIndex: number, subject: string, year: string, isChecked: boolean) => {
    setSelectedSubjects((prev) => {
      const updated: SelectedSubjectsState = { ...prev }

      if (!updated[sectionIndex]) {
        updated[sectionIndex] = {}
      }

      if (isChecked) {
        updated[sectionIndex] = {
          ...updated[sectionIndex],
          [subject]: [...(updated[sectionIndex][subject] || []), year],
        }
      } else {
        updated[sectionIndex] = {
          ...updated[sectionIndex],
          [subject]: (updated[sectionIndex][subject] || []).filter((y) => y !== year),
        }
        if (updated[sectionIndex][subject]?.length === 0) {
          delete updated[sectionIndex][subject]
        }
      }

      return updated
    })
  }

  const handleSubmit = async (formattedSelectedSubjects: SubjectYear[]) => {
    if (!input.trim()) {
      throw new Error('Please enter a question, topic, or keyword to search.')
    }

    if (Object.keys(selectedSubjects).length === 0) {
      throw new Error('Please select at least one year from at least one subject')
    }

    setIsLoading(true)
    setQuestions([])

    try {
      const data = await searchQuestions({
        q: input.trim(),
        search_items: formattedSelectedSubjects,
      })

      setQuestions(data.result || [])
      return data.result || []
    } finally {
      setIsLoading(false)
    }
  }

  const handleSelectAllSubjects = (sections: Array<{ subjects: Record<string, string[]> }>) => {
    setSelectedSubjects(() => {
      const updated: SelectedSubjectsState = {}

      sections.forEach((section, sectionIndex) => {
        updated[sectionIndex] = {}

        Object.keys(section.subjects).forEach((subject) => {
          updated[sectionIndex] = {
            ...updated[sectionIndex],
            [subject]: [...section.subjects[subject]],
          }
        })
      })

      return updated
    })
  }

  const handleResetAllSubjects = () => {
    setSelectedSubjects({})
  }

  const handleSelectAllForSubject = (sectionIndex: number, subject: string, allYears: string[]) => {
    setSelectedSubjects((prev) => ({
      ...prev,
      [sectionIndex]: {
        ...prev[sectionIndex],
        [subject]: allYears,
      },
    }))
  }

  const handleResetForSubject = (sectionIndex: number, subject: string) => {
    setSelectedSubjects((prev) => {
      const updated: SelectedSubjectsState = { ...prev }
      if (updated[sectionIndex]) {
        const section = { ...updated[sectionIndex] }
        delete section[subject]
        updated[sectionIndex] = section
      }
      return updated
    })
  }

  const isAllSelected = (sections: Array<{ subjects: Record<string, string[]> }>) => {
    return sections.every((section, sectionIndex) => {
      const allSubjects = Object.keys(section.subjects)
      return allSubjects.every(
        (subject) =>
          selectedSubjects[sectionIndex]?.[subject]?.length ===
          section.subjects[subject].length
      )
    })
  }

  return {
    input,
    setInput,
    selectedSubjects,
    questions,
    isLoading,
    handleYearChange,
    handleSubmit,
    handleSelectAllSubjects,
    handleResetAllSubjects,
    handleSelectAllForSubject,
    handleResetForSubject,
    isAllSelected,
  }
}

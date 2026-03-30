import { useState } from 'react'
import {
  ChevronLeftCircle,
  ChevronRightCircle,
  ChevronDown,
} from 'lucide-react'
import { ToastContainer, toast } from 'react-toastify'
import 'react-toastify/dist/ReactToastify.css'
import { subjectSections } from '../data/subjects'
import { useSearchForm } from '../hooks/useSearchForm'
import ExamQuestion from './ExamQuestion'

export default function ExamQuestionFinder() {
  const [currentSection, setCurrentSection] = useState(0)
  const [displayedQuestions, setDisplayedQuestions] = useState(5)

  const {
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
  } = useSearchForm()

  const handleShowMore = () => {
    setDisplayedQuestions((prev) => prev + 5)
  }

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    const formattedSelectedSubjects = Object.keys(selectedSubjects)
      .map((sectionKey) => {
        return Object.keys(selectedSubjects[sectionKey]!).map((subject) => ({
          subject: subject,
          years: [...new Set(selectedSubjects[sectionKey]![subject])],
        }))
      })
      .flat()

    try {
      await handleSubmit(formattedSelectedSubjects)
      toast.success('Got Results!')
    } catch (error) {
      toast.error(error instanceof Error ? error.message : 'An error occurred')
    }
  }

  const currentSubjects = subjectSections[currentSection]?.subjects || {}

  const isSubjectFullySelected = (subject: string) => {
    const subjectYears = currentSubjects[subject] || []
    return [...new Set(selectedSubjects[currentSection]?.[subject] || [])]?.length === subjectYears.length
  }

  const isSubjectPartiallySelected = (subject: string) => {
    const subjectYears = currentSubjects[subject] || []
    const selectedYears = [...new Set(selectedSubjects[currentSection]?.[subject] || [])] || []
    return selectedYears.length > 0 && selectedYears.length < subjectYears.length
  }

  const renderSubjectStatus = (subject: string) => {
    if (isSubjectFullySelected(subject)) return 'Fully Selected'
    if (isSubjectPartiallySelected(subject)) return 'Partially Selected'
    return 'Not Selected'
  }

  return (
    <div className="space-y-10 bg-gray-50">
      <ToastContainer />

      <form onSubmit={onSubmit} className="space-y-6">
        {/* Search Input */}
        <textarea
          placeholder="Enter your question, topic, or keyword here... (required)"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onInput={(e) => {
            e.currentTarget.style.height = 'auto'
            e.currentTarget.style.height = `${e.currentTarget.scrollHeight}px`
          }}
          className="w-full min-h-[40px] border border-black focus:border-primary p-4 rounded-xl resize-none overflow-y-hidden"
        />

        {/* Controls */}
        <div className="flex items-center space-x-4 justify-between px-1">
          <label className="inline-flex items-center gap-2">
            <input
              type="checkbox"
              className="size-5 rounded border-gray-300 cursor-pointer hidden"
              onChange={(e) => {
                if (e.currentTarget.checked) {
                  handleSelectAllSubjects(subjectSections)
                } else {
                  handleResetAllSubjects()
                }
              }}
              checked={isAllSelected(subjectSections)}
            />
            <span className="text-sm font-medium text-gray-700 cursor-pointer hover:underline underline-offset-2">
              {isAllSelected(subjectSections) ? 'Deselect All Subjects' : 'Select All Subjects'}
            </span>
          </label>

          <div className="flex justify-between px-2 space-x-2">
            <button
              type="button"
              onClick={() => setCurrentSection((prev) => Math.max(prev - 1, 0))}
              disabled={currentSection === 0}
              className="bg-transparent disabled:opacity-70 transition-all fill-black"
            >
              <ChevronLeftCircle className="w-7 h-7" />
            </button>

            <button
              type="button"
              onClick={() => setCurrentSection((prev) => Math.min(prev + 1, subjectSections.length - 1))}
              disabled={currentSection === subjectSections.length - 1}
              className="bg-transparent fill-black disabled:opacity-70 transition-all"
            >
              <ChevronRightCircle className="w-7 h-7" />
            </button>
          </div>
        </div>

        {/* Subject Selector */}
        <div className="space-y-2">
          {Object.keys(currentSubjects).map((subject) => (
            <details
              key={subject}
              className="overflow-hidden rounded-xl border-2 border-gray-300 focus:border-black [&_summary::-webkit-details-marker]:hidden"
            >
              <summary className="flex cursor-pointer items-center justify-between gap-2 bg-white p-4 text-gray-900 transition-all">
                <span className="text-sm font-medium">{subject}</span>
                <div className="flex items-center justify-between space-x-2">
                  <span className="text-xs font-medium text-gray-500">
                    {renderSubjectStatus(subject)}
                  </span>
                  <ChevronDown className="w-4 h-4" />
                </div>
              </summary>
              <div className="border-t border-gray-200 bg-white">
                <div className="p-4 flex items-center gap-4">
                  <button
                    type="button"
                    onClick={() => handleSelectAllForSubject(currentSection, subject, currentSubjects[subject])}
                    className="text-sm text-gray-900 underline underline-offset-4"
                  >
                    Select All
                  </button>
                  <button
                    type="button"
                    onClick={() => handleResetForSubject(currentSection, subject)}
                    className="text-sm text-gray-900 underline underline-offset-4"
                  >
                    Reset
                  </button>
                </div>
                <ul className="flex flex-wrap gap-2 border-gray-200 p-4 justify-between">
                  {currentSubjects[subject].map((year) => (
                    <li key={year} className="flex items-center">
                      <label className="inline-flex items-center gap-2">
                        <input
                          type="checkbox"
                          className="size-5 rounded border-gray-300"
                          onChange={(e) => handleYearChange(currentSection, subject, year, e.currentTarget.checked)}
                          checked={(selectedSubjects[currentSection]?.[subject] || []).includes(year)}
                        />
                        <span className="text-sm font-medium text-gray-700">{year}</span>
                      </label>
                    </li>
                  ))}
                </ul>
              </div>
            </details>
          ))}
        </div>

        {/* Submit Button */}
        <button
          type="submit"
          className="w-full bg-white text-black py-2 rounded-md transition-all font-medium border-black border-2 active:ring-2 ring-black active:ring-offset-4 outline-none disabled:opacity-50"
          disabled={isLoading}
        >
          {isLoading ? 'Searching...' : 'Search'}
        </button>
      </form>

      {/* Results */}
      <div className="space-y-6">
        {questions.slice(0, displayedQuestions).map((question, index) => (
          <ExamQuestion key={`${question.subject}-${question.year}-${index}`} question={question} />
        ))}
      </div>

      {/* Show More Button */}
      {questions.length > displayedQuestions && (
        <button
          onClick={handleShowMore}
          className="w-full bg-white text-black py-2 rounded-md hover:bg-black hover:text-white transition-all border-black border-2"
        >
          Show More
        </button>
      )}
    </div>
  )
}

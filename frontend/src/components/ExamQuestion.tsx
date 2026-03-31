import { useState, useEffect } from 'react'
import { BookOpen } from 'lucide-react'
import type { Question } from '../types'

export default function ExamQuestion({ question }: { question: Question }) {
  const [explanationHTML, setExplanationHTML] = useState("")
  const [showExplanation, setShowExplanation] = useState(false)

  useEffect(() => {
    if (question.explanation_html) {
      setExplanationHTML(question.explanation_html)
    }
  }, [question.explanation_html])

  const toggleExplanation = () => {
    setShowExplanation((prev) => !prev)
  }

  return (
    <div className="bg-white border border-gray-300 rounded-md shadow-md hover:shadow-lg transition-shadow duration-300">
      <div className="p-6">
        {/* Header */}
        <div className="flex items-center gap-2 text-lg font-semibold text-black">
          <BookOpen className="w-5 h-5" />
          <span>{question.exam_type} {question.year} - {question.subject}</span>
        </div>

        {/* Image (if exists) */}
        {question.image_url && (
          <div className="mt-4">
            <img
              src={question.image_url}
              alt="Question-related visual content"
              className="w-full h-auto max-w-full mx-auto rounded-md shadow-md"
            />
          </div>
        )}

        {/* Question */}
        <div className="mt-4">
          <div className="text-gray-700">
            {question.question}
          </div>

          {/* Options as bullet points */}
          {question.options && (
            <ul className="mt-4 space-y-2 list-disc list-inside">
              {question.options.map((option, index) => (
                <li key={index} className="text-gray-700 ml-4">
                  {option}
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>

      {/* Answer Section */}
      <div className="px-6 py-4 bg-gray-50 border-t border-gray-200">
        {/* Explanation */}
        {showExplanation && explanationHTML && (
          <div className="mb-4 p-4 bg-gray-100 rounded-md border border-gray-300">
            <h4 className="font-semibold text-black mb-2 flex items-center gap-2">
              <BookOpen className="w-4 h-4" />
              Explanation
            </h4>
            <div
              className="text-gray-700 prose prose-sm max-w-none"
              dangerouslySetInnerHTML={{ __html: explanationHTML }}
            />
          </div>
        )}

        {/* Display correct answer if it exists */}
        {showExplanation && question.correct_answer && (
          <div className="mb-4 p-4 bg-gray-200 rounded-md border border-gray-400">
            <h4 className="font-semibold text-black mb-1">Correct Answer</h4>
            <p className="text-gray-800">
               {question.correct_answer.replace(/Correct Answer:\s*/i, '').replace(/^[A-D]\.\s*/, '').trim()}
            </p>
          </div>
        )}

        {/* Toggle Button */}
        {(question.explanation_html || question.correct_answer) && (
          <button
            onClick={toggleExplanation}
            className="w-full bg-black hover:bg-gray-800 text-white py-2 px-4 rounded-md font-medium transition-all flex items-center justify-center gap-2"
          >
            <BookOpen className="w-4 h-4" />
            {showExplanation ? "Hide Answer" : "Show Answer"}
          </button>
        )}

        {!question.explanation_html && !question.correct_answer && (
          <div className="text-center text-gray-500 text-sm py-2">
            No explanation or correct answer available
          </div>
        )}
      </div>
    </div>
  )
}

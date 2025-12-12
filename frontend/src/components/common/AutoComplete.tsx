import { useState, useRef, useEffect } from 'react'

interface AutoCompleteOption {
  id: number | string
  label: string
  value: string
}

interface AutoCompleteProps {
  options: AutoCompleteOption[]
  value: number | string | ''
  onChange: (value: number | string) => void
  placeholder?: string
  disabled?: boolean
  required?: boolean
  label?: string
  error?: string
  filterFn?: (option: AutoCompleteOption, query: string) => boolean
}

export default function AutoComplete({
  options,
  value,
  onChange,
  placeholder = 'ابدأ بالكتابة...',
  disabled = false,
  required = false,
  label,
  error,
  filterFn,
}: AutoCompleteProps) {
  const [isOpen, setIsOpen] = useState(false)
  const [query, setQuery] = useState('')
  const [filteredOptions, setFilteredOptions] = useState<AutoCompleteOption[]>(options)
  const inputRef = useRef<HTMLInputElement>(null)
  const dropdownRef = useRef<HTMLDivElement>(null)

  // العثور على الخيار المحدد
  const selectedOption = options.find((opt) => opt.id === value)

  // تحديث القائمة المفلترة عند تغيير الاستعلام
  useEffect(() => {
    if (query.trim() === '') {
      setFilteredOptions(options)
    } else {
      const filtered = options.filter((option) => {
        if (filterFn) {
          return filterFn(option, query)
        }
        return option.label.toLowerCase().includes(query.toLowerCase()) ||
               option.value.toLowerCase().includes(query.toLowerCase())
      })
      setFilteredOptions(filtered)
    }
  }, [query, options, filterFn])

  // إغلاق القائمة عند النقر خارجها
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        dropdownRef.current &&
        !dropdownRef.current.contains(event.target as Node) &&
        inputRef.current &&
        !inputRef.current.contains(event.target as Node)
      ) {
        setIsOpen(false)
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    return () => {
      document.removeEventListener('mousedown', handleClickOutside)
    }
  }, [])

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newQuery = e.target.value
    setQuery(newQuery)
    setIsOpen(true)

    // إذا تم مسح الحقل، إلغاء التحديد
    if (newQuery === '') {
      onChange('')
    }
  }

  const handleSelect = (option: AutoCompleteOption) => {
    onChange(option.id)
    setQuery(option.label)
    setIsOpen(false)
  }

  const handleFocus = () => {
    setIsOpen(true)
    if (selectedOption) {
      setQuery(selectedOption.label)
    }
  }

  const handleBlur = () => {
    // تأخير الإغلاق للسماح بالنقر على الخيار
    setTimeout(() => {
      setIsOpen(false)
      if (selectedOption) {
        setQuery(selectedOption.label)
      } else {
        setQuery('')
      }
    }, 200)
  }

  return (
    <div className="relative">
      {label && (
        <label className="block text-sm font-medium text-gray-700 mb-1">
          {label} {required && <span className="text-red-500">*</span>}
        </label>
      )}
      <div className="relative">
        <input
          ref={inputRef}
          type="text"
          value={query}
          onChange={handleInputChange}
          onFocus={handleFocus}
          onBlur={handleBlur}
          placeholder={placeholder}
          disabled={disabled}
          required={required}
          className={`input-field ${error ? 'border-red-500' : ''} ${disabled ? 'bg-gray-100 cursor-not-allowed' : ''}`}
        />
        {isOpen && filteredOptions.length > 0 && !disabled && (
          <div
            ref={dropdownRef}
            className="absolute z-50 w-full mt-1 bg-white border border-gray-300 rounded-lg shadow-lg max-h-60 overflow-auto"
          >
            {filteredOptions.map((option) => (
              <div
                key={option.id}
                onClick={() => handleSelect(option)}
                className={`px-4 py-2 cursor-pointer hover:bg-blue-50 ${
                  value === option.id ? 'bg-blue-100' : ''
                }`}
              >
                {option.label}
              </div>
            ))}
          </div>
        )}
        {isOpen && filteredOptions.length === 0 && query.trim() !== '' && (
          <div className="absolute z-50 w-full mt-1 bg-white border border-gray-300 rounded-lg shadow-lg">
            <div className="px-4 py-2 text-gray-500 text-sm">لا توجد نتائج</div>
          </div>
        )}
      </div>
      {error && <p className="mt-1 text-sm text-red-600">{error}</p>}
    </div>
  )
}

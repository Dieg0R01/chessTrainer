import { useState, useRef, useEffect } from 'react';

function CustomSelect({ value, onChange, options, placeholder = "Selecciona..." }) {
  const [isOpen, setIsOpen] = useState(false);
  const selectRef = useRef(null);
  const dropdownRef = useRef(null);

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (
        selectRef.current &&
        !selectRef.current.contains(event.target) &&
        dropdownRef.current &&
        !dropdownRef.current.contains(event.target)
      ) {
        setIsOpen(false);
      }
    };

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [isOpen]);

  const selectedOption = options.find(opt => opt.value === value) || null;
  const displayText = selectedOption ? selectedOption.label : placeholder;

  const handleSelect = (optionValue) => {
    onChange(optionValue);
    setIsOpen(false);
  };

  // Calcular posición del dropdown relativa al contenedor padre
  useEffect(() => {
    if (isOpen && selectRef.current && dropdownRef.current) {
      const rect = selectRef.current.getBoundingClientRect();
      const dropdown = dropdownRef.current;
      const container = selectRef.current.parentElement;
      
      if (container) {
        const containerRect = container.getBoundingClientRect();
        
        // Calcular posición relativa al contenedor
        const relativeTop = rect.bottom - containerRect.top + 5;
        const relativeLeft = rect.left - containerRect.left;
        
        dropdown.style.top = `${relativeTop}px`;
        dropdown.style.left = `${relativeLeft}px`;
        dropdown.style.width = `${rect.width}px`;
      }
    }
  }, [isOpen]);

  return (
    <div style={{ position: 'relative', width: '100%' }}>
      <div
        ref={selectRef}
        className="custom-select-trigger"
        onClick={() => setIsOpen(!isOpen)}
        style={{
          fontFamily: 'VT323, monospace',
          fontSize: '24px',
          padding: '15px 12px',
          background: 'transparent',
          color: 'var(--retro-green)',
          border: '2px solid var(--retro-green)',
          borderRadius: '0',
          letterSpacing: '1.5px',
          width: '100%',
          cursor: 'pointer',
          position: 'relative',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
        }}
      >
        <span>{displayText}</span>
        <span style={{ fontSize: '16px', marginLeft: '10px' }}>{isOpen ? '▲' : '▼'}</span>
      </div>

      {isOpen && (
        <>
          <div
            className="custom-select-overlay"
            onClick={() => setIsOpen(false)}
            style={{
              position: 'fixed',
              top: 0,
              left: 0,
              right: 0,
              bottom: 0,
              zIndex: 9998,
              background: 'transparent',
            }}
          />
          <div
            ref={dropdownRef}
            className="custom-select-dropdown"
            style={{
              position: 'absolute',
              zIndex: 9999,
              background: 'linear-gradient(to bottom, rgba(0, 40, 0, 0.98), rgba(0, 20, 0, 0.98))',
              border: '2px solid var(--retro-green)',
              borderRadius: '0',
              boxShadow: '0 0 20px var(--retro-glow), inset 0 0 20px rgba(0, 0, 0, 0.5)',
              maxHeight: '300px',
              overflowY: 'auto',
              padding: '5px 0',
            }}
          >
            {options.map((option) => (
              <div
                key={option.value}
                className="custom-select-option"
                onClick={() => handleSelect(option.value)}
                style={{
                  fontFamily: 'VT323, monospace',
                  fontSize: '24px',
                  padding: '12px 15px',
                  color: 'var(--retro-green)',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '10px',
                  letterSpacing: '1.5px',
                  transition: 'all 0.1s',
                }}
                onMouseEnter={(e) => {
                  e.target.style.background = 'rgba(51, 255, 51, 0.1)';
                  e.target.style.boxShadow = '0 0 10px var(--retro-glow)';
                }}
                onMouseLeave={(e) => {
                  e.target.style.background = 'transparent';
                  e.target.style.boxShadow = 'none';
                }}
              >
                <div
                  className="custom-select-radio"
                  style={{
                    width: '16px',
                    height: '16px',
                    border: '2px solid var(--retro-green)',
                    borderRadius: '50%',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    flexShrink: 0,
                  }}
                >
                  {value === option.value && (
                    <div
                      style={{
                        width: '10px',
                        height: '10px',
                        borderRadius: '50%',
                        background: 'var(--retro-green)',
                        boxShadow: '0 0 8px var(--retro-glow)',
                      }}
                    />
                  )}
                </div>
                <span>{option.label}</span>
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  );
}

export default CustomSelect;


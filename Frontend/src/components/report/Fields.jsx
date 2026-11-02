import { cn } from "../../lib/utils";

// Form primitives for the report wizard. Every input is labelled, shows its hint under the
// label, and shows its error in place, so a student never has to guess what is wrong.

const inputBase =
    "w-full bg-white border-3 border-black px-3 py-3 text-base font-mono outline-none focus:shadow-neo focus:bg-yellow-50 disabled:bg-gray-100 disabled:text-gray-700 disabled:cursor-not-allowed";

export const Field = ({ id, label, required, hint, error, warning, children, className }) => (
    <div className={className}>
        <label htmlFor={id} className="block font-bold uppercase text-sm mb-1">
            {label} {required && <span className="text-red-600" aria-hidden>*</span>}
        </label>
        {hint && <p id={`${id}-hint`} className="text-xs text-black/60 mb-2 leading-snug">{hint}</p>}
        {children}
        {error && <p id={`${id}-error`} className="mt-1 text-sm font-bold text-red-700">{error}</p>}
        {!error && warning && <p className="mt-1 text-sm text-amber-700">{warning}</p>}
    </div>
);

const describedBy = (id, hint, error) =>
    [hint && `${id}-hint`, error && `${id}-error`].filter(Boolean).join(" ") || undefined;

export const TextInput = ({ id, value, onChange, error, hint, className, ...rest }) => (
    <input
        id={id}
        value={value ?? ""}
        onChange={(e) => onChange(e.target.value)}
        aria-invalid={Boolean(error)}
        aria-describedby={describedBy(id, hint, error)}
        className={cn(inputBase, error && "border-red-600 bg-red-50", className)}
        {...rest}
    />
);

export const TextArea = ({ id, value, onChange, error, hint, rows = 4, className, ...rest }) => (
    <textarea
        id={id}
        value={value ?? ""}
        rows={rows}
        onChange={(e) => onChange(e.target.value)}
        aria-invalid={Boolean(error)}
        aria-describedby={describedBy(id, hint, error)}
        className={cn(inputBase, "leading-relaxed", error && "border-red-600 bg-red-50", className)}
        {...rest}
    />
);

export const Select = ({ id, value, onChange, options, placeholder, error, hint }) => (
    <select
        id={id}
        value={value ?? ""}
        onChange={(e) => onChange(e.target.value)}
        aria-invalid={Boolean(error)}
        aria-describedby={describedBy(id, hint, error)}
        className={cn(inputBase, "font-bold", error && "border-red-600 bg-red-50")}
    >
        {placeholder && <option value="" disabled>{placeholder}</option>}
        {options.map(o => (
            <option key={o.value ?? o} value={o.value ?? o}>{o.label ?? o}</option>
        ))}
    </select>
);

export const Card = ({ className, children }) => (
    <div className={cn("bg-white border-3 border-black p-4 md:p-6", className)}>{children}</div>
);

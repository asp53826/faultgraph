interface StatusMarkProps {
  tone: "fault" | "confirmed" | "trace" | "contradiction" | "quiet";
  label: string;
}

export function StatusMark({ tone, label }: StatusMarkProps) {
  return (
    <span className={`status-mark status-mark--${tone}`}>
      <span className="status-mark__pin" aria-hidden="true" />
      {label}
    </span>
  );
}

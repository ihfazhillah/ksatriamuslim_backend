export const formatCurrency = (
  amount: number | null | undefined,
  currency: "USD" | "IDR" = "USD"
): string => {
  // Handle null, undefined, or NaN values
  if (amount == null || isNaN(amount)) {
    amount = 0;
  }

  const locale = currency === "USD" ? "en-US" : "id-ID";

  return new Intl.NumberFormat(locale, {
    style: "currency",
    currency: currency,
    minimumFractionDigits: currency === "USD" ? 2 : 0,
    maximumFractionDigits: currency === "USD" ? 2 : 0,
  }).format(amount);
};

export const formatDate = (date: string | Date | null | undefined): string => {
  if (!date) return "-";

  const dateObj = typeof date === "string" ? new Date(date) : date;

  // Check if the date is valid
  if (isNaN(dateObj.getTime())) {
    return "-";
  }

  return new Intl.DateTimeFormat("en-US", {
    year: "numeric",
    month: "short",
    day: "numeric",
  }).format(dateObj);
};

export const formatDateTime = (
  date: string | Date | null | undefined
): string => {
  if (!date) return "-";

  const dateObj = typeof date === "string" ? new Date(date) : date;

  // Check if the date is valid
  if (isNaN(dateObj.getTime())) {
    return "-";
  }

  return new Intl.DateTimeFormat("en-US", {
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  }).format(dateObj);
};

export const formatHours = (hours: number | null | undefined): string => {
  // Handle null, undefined, or NaN values
  if (hours == null || isNaN(hours)) {
    return "0h";
  }

  const wholeHours = Math.floor(hours);
  const minutes = Math.round((hours - wholeHours) * 60);

  if (minutes === 0) {
    return `${wholeHours}h`;
  }

  return `${wholeHours}h ${minutes}m`;
};

export const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return "0 Bytes";

  const k = 1024;
  const sizes = ["Bytes", "KB", "MB", "GB"];
  const i = Math.floor(Math.log(bytes) / Math.log(k));

  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i];
};

export const formatClientAddress = (client: {
  address_line1?: string;
  address_line2?: string;
  address_line3?: string;
  address_line4?: string;
}): string => {
  const lines = [
    client.address_line1,
    client.address_line2,
    client.address_line3,
    client.address_line4,
  ].filter(Boolean);

  return lines.join(", ") || "-";
};

// Parse datetime format like "202506241333" to proper Date
export const parseClockifyDateTime = (dateTimeStr: string): Date | null => {
  if (!dateTimeStr || dateTimeStr.length !== 12) {
    return null;
  }

  // Format: YYYYMMDDHHMM (202506241333)
  const year = parseInt(dateTimeStr.substring(0, 4));
  const month = parseInt(dateTimeStr.substring(4, 6)) - 1; // Month is 0-indexed
  const day = parseInt(dateTimeStr.substring(6, 8));
  const hour = parseInt(dateTimeStr.substring(8, 10));
  const minute = parseInt(dateTimeStr.substring(10, 12));

  const date = new Date(year, month, day, hour, minute);

  // Check if the date is valid
  if (isNaN(date.getTime())) {
    return null;
  }

  return date;
};

// Format clockify datetime string to readable format
export const formatClockifyDateTime = (dateTimeStr: string): string => {
  const date = parseClockifyDateTime(dateTimeStr);
  if (!date) return "-";

  return formatDateTime(date);
};

// Parse duration hours from string like "0.92" to formatted duration
export const formatDurationFromHours = (hoursStr: string | number): string => {
  if (!hoursStr) return "0h";

  const hours = typeof hoursStr === "string" ? parseFloat(hoursStr) : hoursStr;
  if (isNaN(hours)) return "0h";

  return formatHours(hours);
};

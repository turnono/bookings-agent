import { Pipe, PipeTransform } from '@angular/core';
import { DomSanitizer, SafeHtml } from '@angular/platform-browser';

@Pipe({
  name: 'formatMessage',
  standalone: true,
})
export class FormatMessagePipe implements PipeTransform {
  constructor(private sanitizer: DomSanitizer) {}

  transform(text: string): SafeHtml {
    if (!text) return '';

    // Handle tables (lines with | characters)
    const tableRegex = /^\|(.*\|)+$/gm;
    if (tableRegex.test(text)) {
      const lines = text.split('\n');
      let tableHtml = '<table class="formatted-table"><tbody>';
      let isHeader = true;

      for (const line of lines) {
        // Skip separator lines with --- (Header/body separator)
        if (line.match(/^\|(\s*[-]+\s*\|)+$/)) {
          isHeader = false;
          continue;
        }

        // Process actual table rows
        if (line.match(/^\|(.*\|)+$/)) {
          const cells = line.split('|').filter((cell) => cell.length); // Remove empty first/last entries

          if (isHeader) {
            tableHtml += '<tr>';
            cells.forEach((cell) => {
              tableHtml += `<th>${cell.trim()}</th>`;
            });
            tableHtml += '</tr>';
          } else {
            tableHtml += '<tr>';
            cells.forEach((cell) => {
              tableHtml += `<td>${cell.trim()}</td>`;
            });
            tableHtml += '</tr>';
          }
        }
      }

      tableHtml += '</tbody></table>';

      // Replace the original table text with HTML
      text = text.replace(/^(\|(.*\|)+\n?)+$/gm, tableHtml);
    }

    // Handle bullet point lists (lines starting with * or -)
    text = text.replace(/^[*-]\s(.+)$/gm, '<li>$1</li>');
    text = text.replace(/<li>(.+)<\/li>/g, function (match) {
      if (match.includes('<ul>') || match.includes('</ul>')) return match;
      return '<ul>' + match + '</ul>';
    });

    // Handle numbered lists
    text = text.replace(/^\d+\.\s(.+)$/gm, '<li>$1</li>');
    text = text.replace(/<li>(.+)<\/li>/g, function (match) {
      if (match.includes('<ol>') || match.includes('</ol>')) return match;
      return '<ol>' + match + '</ol>';
    });

    // Convert line breaks to <br>
    text = text.replace(/\n/g, '<br>');

    // Bold text between ** markers
    text = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');

    // Italic text between * markers (not at list items)
    text = text.replace(/\*([^*]+)\*/g, '<em>$1</em>');

    // Auto-link URLs that aren't already in anchor tags
    const urlRegex = /(https?:\/\/[^\s<]+)/g;
    text = text.replace(urlRegex, (url) => {
      // Don't process URLs that are already in html tags
      if (url.includes('href=') || url.includes('src=')) return url;
      return `<a href="${url}" target="_blank" rel="noopener noreferrer">${url}</a>`;
    });

    return this.sanitizer.bypassSecurityTrustHtml(text);
  }
}

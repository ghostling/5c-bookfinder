$(document).ready(function() {
  var courses, books;

  // Initialize the autocompletion of courses.
  courses = new Bloodhound({
    datumTokenizer: function(obj) {
      var title = Bloodhound.tokenizers.whitespace(obj.title);
      var num = Bloodhound.tokenizers.whitespace(obj.course_number)
      var prof = Bloodhound.tokenizers.whitespace(obj.professor);

      var merged = [];
      merged = merged.concat(title, num, prof);
      return merged;
    },
    queryTokenizer: Bloodhound.tokenizers.whitespace,
    prefetch: {
      url: '../static/js/custom/courses.json'
    }
  });
  courses.initialize();

  // Then, initialize the autocompletion of books.
  books = new Bloodhound({
    datumTokenizer: function(obj) {
      var isbn = obj.book_isbn;
      var author = Bloodhound.tokenizers.whitespace(obj.author)
      var title = Bloodhound.tokenizers.whitespace(obj.title);

      var merged = [];
      merged = merged.concat(isbn, author, title);
      return merged;
    },
    queryTokenizer: Bloodhound.tokenizers.whitespace,
    prefetch: {
      url: '../static/js/custom/books.json'
    }
  });
  books.initialize();

  // Then, initialize the typeahead.
  $('.typeahead').typeahead(null, [
    {
      name: 'courses',
      source: courses.ttAdapter(),
      //displayKey: 'title',
      templates: {
        suggestion: function (context) {
          return "<p>" + context.title + " (" + context.professor + ")<span class=\"right\"><strong>Course</strong></span><br />" + 
          context.course_number + "</p>";
        }
      }
    },
    
    {
      name: 'books',
      source: books.ttAdapter(),
      displayKey: 'name',
      templates: {
      suggestion: function suggestionTemplate(context) {
          return "<p>" + context.title + " (" + context.author + ")<span class=\"right\"><strong>Book</strong></span><br />" + 
          context.book_isbn + "</p>";
        }
      }
    }
  ]);

  // Add an event listener that redirects user to the proper page on a suggestion click.
  $('.typeahead').bind('typeahead:selected', function(obj, datum, name) {
    if (name == 'courses') {
      window.location.href = '/course/' + datum.course_number;
    } else if (name == 'books') {
      window.location.href = '/book/' + datum.book_isbn;
    }
  });
});

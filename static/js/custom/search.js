$(document).ready(function() {
  var courses, books;

  // Initialize the autocompletion of courses.
  courses = new Bloodhound({
    datumTokenizer: Bloodhound.tokenizers.obj.whitespace('name'),
    queryTokenizer: Bloodhound.tokenizers.whitespace,
    prefetch: {
      url: '../static/js/custom/courses.json',
      filter: function(list) {
        return $.map(list, function (classVal) {
          return { name: classVal.course_number }
        });
      }
    }
  });
  courses.initialize();

  // Then, initialize the autocompletion of books.
  books = new Bloodhound({
    datumTokenizer: Bloodhound.tokenizers.obj.whitespace('name'),
    queryTokenizer: Bloodhound.tokenizers.whitespace,
    prefetch: {
      url: '../static/js/custom/books.json',
      filter: function(list) {
        return $.map(list, function (classVal) {
          return { name: classVal.title }
        });
      }
    }
  });
  books.initialize();

  $('.typeahead').typeahead(null, [
    {
      name: 'courses',
      source: courses.ttAdapter(),
      displayKey: 'name'
    },
    
    {
      name: 'books',
      source: books.ttAdapter(),
      displayKey: 'name'
    }
  ]);
});

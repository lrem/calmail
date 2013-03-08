$ ->
    $.getJSON 'https://www-sop.inria.fr/members/Remigiusz.Modrzejewski/seminars.json', (data) -> 
        content = '<div class="entry-content clearfix">'
        for e in data
            slides = if not e['SLIDES'] then '' else \
                "<p><a href=\"#{e['SLIDES']}\">Slides</a></p>"
            content += "
            <p>&nbsp;</p>
            <a href=\"#{e['URL']}\">#{e['AUTHOR']}</a>
            (#{e['AFFILIATION']})
            &mdash;
            #{e['DATE']}
            <blockquote>
            <p><strong>#{e['SUMMARY']}</strong></p>
            #{slides}
            <p>
            #{e['ABSTRACT']}
            </p>
            </blockquote>"
        content += '</div>'
        div = $('div.entry-content')
        div.replaceWith content

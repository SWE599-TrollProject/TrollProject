(function ($) {

    $('.bot.circle').circleProgress({
        value: 0,
        lineCap: 'round',
        fill: {gradient: ['#ff1e41', '#ff5f43']}
    }).on('circle-animation-progress', function (event, progress, stepValue) {
        $(this).find('strong').text(stepValue.toFixed(2).substr(2));
    });

    $('.activity.circle').circleProgress({
        value: 0,
        lineCap: 'round'
    }).on('circle-animation-progress', function (event, progress, stepValue) {
        $(this).find('strong').text(stepValue.toFixed(2).substr(2));
    });

    $('.toxicity.circle').circleProgress({
        value: 0,
        lineCap: 'round',
        fill: {gradient: ['#ff1e41', '#ff5f43']}
    }).on('circle-animation-progress', function (event, progress, stepValue) {
        $(this).find('strong').text(stepValue.toFixed(2).substr(2));
    });


    $('.spam.circle').circleProgress({
        value: 0,
        lineCap: 'round'
    }).on('circle-animation-progress', function (event, progress, stepValue) {
        $(this).find('strong').text(stepValue.toFixed(2).substr(2));
    });


    $('.inflammatory.circle').circleProgress({
        value: 0,
        lineCap: 'round',
        fill: {gradient: ['#0681c4', '#4ac5f8']}
    }).on('circle-animation-progress', function (event, progress, stepValue) {
        $(this).find('strong').text(stepValue.toFixed(2).substr(2));
    });

    $('.obscenity.circle').circleProgress({
        startAngle: -Math.PI / 4 * 3,
        value: 0,
        lineCap: 'round',
        fill: {color: '#ffa500'}
    }).on('circle-animation-progress', function (event, progress, stepValue) {
        $(this).find('strong').text(stepValue.toFixed(2).substr(2));
    });

    var form = $('#searchForm');
    form.submit(function (e) {
        e.preventDefault();
        $.ajax({
            type: "POST",
            url: "/search",
            data: form.serialize(),
            success: function (data) {
                var bot = $('.bot.circle');
                var activity = $('.activity.circle');
                var toxicity = $('.toxicity.circle');
                var spam = $('.spam.circle');
                var inflammatory = $('.inflammatory.circle');
                var obscenity = $('.obscenity.circle');

                var r = JSON.parse(data).result;
                toxicity.circleProgress({value: r.troll_level.TOXICITY});
                spam.circleProgress({value: r.troll_level.SPAM});
                inflammatory.circleProgress({value: r.troll_level.INFLAMMATORY});
                obscenity.circleProgress({value: r.troll_level.OBSCENE});
                activity.circleProgress({value: r.activity_level.tweets_per_day / 100.0});
            },
            error: function (err) {
                console.log(err);
            }
        });
    })

})(jQuery);
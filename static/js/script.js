/*
Author       : Dreamguys
Template Name: Doccure - Bootstrap Template
Version      : 1.3
*/

(function ($) {
	"use strict";

	// Stick Sidebar

	if ($(window).width() > 767) {
		if ($('.theiaStickySidebar').length > 0) {
			$('.theiaStickySidebar').theiaStickySidebar({
				// Settings
				additionalMarginTop: 30
			});
		}
	}

	// Sidebar

	if ($(window).width() <= 991) {
		var Sidemenu = function () {
			this.$menuItem = $('.main-nav a');
		};

		function init() {
			var $this = Sidemenu;
			$('.main-nav a').on('click', function (e) {
				if ($(this).parent().hasClass('has-submenu')) {
					e.preventDefault();
				}
				if (!$(this).hasClass('submenu')) {
					$('ul', $(this).parents('ul:first')).slideUp(350);
					$('a', $(this).parents('ul:first')).removeClass('submenu');
					$(this).next('ul').slideDown(350);
					$(this).addClass('submenu');
				} else if ($(this).hasClass('submenu')) {
					$(this).removeClass('submenu');
					$(this).next('ul').slideUp(350);
				}
			});
		}

		// Sidebar Initiate
		init();
	}

	// Textarea Text Count

	var maxLength = 100;
	$('#review_desc').on('keyup change', function () {
		var length = $(this).val().length;
		length = maxLength - length;
		$('#chars').text(length);
	});

	// Select 2

	if ($('.select').length > 0) {
		$('.select').select2({
			minimumResultsForSearch: -1,
			width: '100%'
		});
	}

	// consultation

	$(".consultation-types").on('click', function () {
		$(".consultation-types").removeClass('active');
		$(this).addClass('active');
	});

	// Date Time Picker

	if ($('.datetimepicker').length > 0) {
		$('.datetimepicker').datetimepicker({
			format: 'DD/MM/YYYY',
			icons: {
				up: "fas fa-chevron-up",
				down: "fas fa-chevron-down",
				next: 'fas fa-chevron-right',
				previous: 'fas fa-chevron-left'
			}
		});
	}

	if ($('.timepicker1').length > 0) {
		$('.timepicker1').datetimepicker({
			format: 'HH:mm A',
			icons: {
				up: "fas fa-angle-up",
				down: "fas fa-angle-down",
				next: 'fas fa-angle-right',
				previous: 'fas fa-angle-left'
			}
		});
	}

	// AOS Animation

	if ($('.main-wrapper .aos').length > 0) {
		AOS.init({
			duration: 1200,
			once: true,
		});
	}

	// Floating Label

	if ($('.floating').length > 0) {
		$('.floating').on('focus blur', function (e) {
			$(this).parents('.form-focus').toggleClass('focused', (e.type === 'focus' || this.value.length > 0));
		}).trigger('blur');
	}

	// Mobile menu sidebar overlay

	$('body').append('<div class="sidebar-overlay"></div>');
	$(document).on('click', '#mobile_btn', function () {
		$('main-wrapper').toggleClass('slide-nav');
		$('.sidebar-overlay').toggleClass('opened');
		$('html').toggleClass('menu-opened');
		return false;
	});

	$(document).on('click', '.sidebar-overlay', function () {
		$('html').removeClass('menu-opened');
		$(this).removeClass('opened');
		$('main-wrapper').removeClass('slide-nav');
	});

	$(document).on('click', '#menu_close', function () {
		$('html').removeClass('menu-opened');
		$('.sidebar-overlay').removeClass('opened');
		$('main-wrapper').removeClass('slide-nav');
	});

	// Tooltip

	if ($('[data-bs-toggle="tooltip"]').length > 0) {
		var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
		var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
			return new bootstrap.Tooltip(tooltipTriggerEl)
		})
	}

	// Add More Hours

	$(".hours-info").on('click', '.trash', function () {
		$(this).closest('.hours-cont').remove();
		return false;
	});

	$(".add-hours").on('click', function () {

		var hourscontent = '<div class="row hours-cont">' +
			'<div class="col-12 col-md-10">' +
			'<div class="row">' +
			'<div class="col-12 col-md-6">' +
			'<div class="forms-block">' +
			'<label>Start Time</label>' +
			'<select class="form-select form-control">' +
			'<option>-</option>' +
			'<option>12.00 am</option>' +
			'<option>12.30 am</option>' +
			'<option>1.00 am</option>' +
			'<option>1.30 am</option>' +
			'</select>' +
			'</div>' +
			'</div>' +
			'<div class="col-12 col-md-6">' +
			'<div class="forms-block">' +
			'<label>End Time</label>' +
			'<select class="form-select form-control">' +
			'<option>-</option>' +
			'<option>12.00 am</option>' +
			'<option>12.30 am</option>' +
			'<option>1.00 am</option>' +
			'<option>1.30 am</option>' +
			'</select>' +
			'</div>' +
			'</div>' +
			'</div>' +
			'</div>' +
			'<div class="col-12 col-md-2"><label class="d-md-block d-sm-none d-none">&nbsp;</label><a href="#" class="btn btn-danger trash"><i class="far fa-trash-alt"></i></a></div>' +
			'</div>';

		$(".hours-info").append(hourscontent);
		return false;
	});

	// Content div min height set

	function resizeInnerDiv() {
		var height = $(window).height();
		var header_height = $(".header").height();
		var footer_height = $(".footer").height();
		var setheight = height - header_height;
		var trueheight = setheight - footer_height;
		$(".content").css("min-height", trueheight);
	}

	if ($('.content').length > 0) {
		resizeInnerDiv();
	}

	$(window).resize(function () {
		if ($('.content').length > 0) {
			resizeInnerDiv();
		}
	});

	// Favourites
	$('.fav-icon').on('click', function () {
		$(this).toggleClass('selected');
		//$(this).children().toggleClass("feather-heart fa-solid fa-heart");
	});
		$('.fav-item').on('click', function () {
		$(this).toggleClass('selected');
		//$(this).children().toggleClass("feather-heart fa-solid fa-heart");
	});

	if ($('.header-eleven').length > 0) {
		$(document).ready(function () {
			$(window).scroll(function () {
				var scroll = $(window).scrollTop();
				if (scroll > 95) {
					$(".header-eleven").css("background", "#1e5d92");
				}

				else {
					$(".header-eleven").css("background", "transparent");
				}
			})
		})
	}

	//owl carousel

	if ($('.owl-carousel.special').length > 0) {
		$('.owl-carousel.special').owlCarousel({
			loop: true,
			margin: 15,
			dots: true,
			nav: true,
			smartSpeed: 2000,
			rtl: true,
			navText: ['<i class="fas fa-chevron-left"></i>', '<i class="fas fa-chevron-right"></i>'],
			responsive: {
				0: {
					items: 1
				},
				500: {
					items: 2
				},
				768: {
					items: 3
				},
				1000: {
					items: 4
				},
				1300: {
					items: 4
				}
			}
		})
	}

	//Eye Clicnic carousel

	if ($('.owl-carousel.eye-clinic').length > 0) {
		$('.owl-carousel.eye-clinic').owlCarousel({
			loop: true,
			margin: 15,
			dots: true,
			nav: true,
			smartSpeed: 2000,
			rtl: true,
			navText: ['<i class="fas fa-chevron-left"></i>', '<i class="fas fa-chevron-right"></i>'],
			responsive: {
				0: {
					items: 1
				},
				500: {
					items: 1
				},
				768: {
					items: 2
				},
				992: {
					items: 3
				},
				1200: {
					items: 4
				}
			}
		})
	}
	//Eye Blog carousel

	if ($('.owl-carousel.eye-blogslider').length > 0) {
		$('.owl-carousel.eye-blogslider').owlCarousel({
			loop: true,
			margin: 15,
			dots: true,
			nav: true,
			smartSpeed: 2000,
			rtl: true,
			navText: ['<i class="fas fa-chevron-left"></i>', '<i class="fas fa-chevron-right"></i>'],
			responsive: {
				0: {
					items: 1
				},
				500: {
					items: 1
				},
				768: {
					items: 2
				},
				1000: {
					items: 3
				},
				1300: {
					items: 4
				}
			}
		})
	}

	//Eye Testimonial carousel

	if ($('.owl-carousel.eye-testislider').length > 0) {
		$('.owl-carousel.eye-testislider').owlCarousel({
			loop: true,
			margin: 15,
			dots: false,
			nav: true,
			smartSpeed: 2000,
			rtl: true,
			navContainer: '.slide-11',
			navText: ['<i class="fa-solid fa-arrow-right"></i>', '<i class="fa-solid fa-arrow-left"></i>'],
			responsive: {
				0: {
					items: 1
				},
				1300: {
					items: 1
				}
			}
		})
	}

	// Specialities Slider

	if ($('.owl-carousel.specialities-slider-one').length > 0) {
		$('.owl-carousel.specialities-slider-one').owlCarousel({
			loop: true,
			margin: 24,
			dots: false,
			nav: true,
			smartSpeed: 2000,
			rtl: true,
			navContainer: '.slide-nav-1',
			navText: ['<i class="fas fa-chevron-left custom-arrow"></i>', '<i class="fas fa-chevron-right custom-arrow"></i>'],
			responsive: {
				0: {
					items: 1
				},
				500: {
					items: 1
				},
				768: {
					items: 2
				},
				1000: {
					items: 3
				},
				1300: {
					items: 6
				}
			}
		})
	}

	// Doctors Slider

	if ($('.owl-carousel.doctor-slider-one').length > 0) {
		$('.owl-carousel.doctor-slider-one').owlCarousel({
			loop: true,
			margin: 24,
			dots: false,
			nav: true,
			rtl: true,
			smartSpeed: 2000,
			navContainer: '.slide-nav-2',
			navText: ['<i class="fas fa-chevron-left custom-arrow"></i>', '<i class="fas fa-chevron-right custom-arrow"></i>'],
			responsive: {
				0: {
					items: 1
				},
				500: {
					items: 1
				},
				768: {
					items: 2
				},
				1000: {
					items: 3
				},
				1300: {
					items: 4
				}
			}
		})
	}

	// Team Slider
	if ($('.owl-carousel.team-fourteen-slider').length > 0) {
		$('.owl-carousel.team-fourteen-slider').owlCarousel({
			loop: true,
			margin: 24,
			dots: false,
			nav: true,
			smartSpeed: 2000,
			navContainer: '.slide-nav-14',
			rtl: true,
			navText: ['<i class="fa-solid fa-caret-right"></i>', '<i class="fa-solid fa-caret-left "></i>'],
			responsive: {
				0: {
					items: 1
				},
				500: {
					items: 1
				},
				768: {
					items: 2
				},
				1000: {
					items: 2
				},
				1300: {
					items: 2
				}
			}
		})
	}

	// Feature Slider
	if ($('.owl-carousel.features-slider-sixteen').length > 0) {
		$('.owl-carousel.features-slider-sixteen').owlCarousel({
			loop: true,
			margin: 24,
			dots: true,
			nav: false,
			smartSpeed: 2000,
			rtl: true,
			responsive: {
				0: {
					items: 1
				},
				500: {
					items: 1
				},
				768: {
					items: 2
				},
				1000: {
					items: 3
				},
				1300: {
					items: 3
				}
			}
		})
	}

	// Blog Slider

	// if ($('.owl-carousel.blog-slider-fourteen').length > 0) {
	// 	$('.owl-carousel.blog-slider-fourteen').owlCarousel({
	// 		loop: true,
	// 		margin: 24,
	// 		dots: false,
	// 		nav: true,
	// 		smartSpeed: 2000,
	// 		rtl: true,
	// 		navContainer: '.slide-nav-15',
	// 		navText: ['<i class="fa-solid fa-caret-right"></i>', '<i class="fa-solid fa-caret-left "></i>'],
	// 		responsive: {
	// 			0: {
	// 				items: 1
	// 			},
	// 			500: {
	// 				items: 1
	// 			},
	// 			575: {
	// 				items: 1
	// 			},
	// 			768: {
	// 				items: 2
	// 			},
	// 			1000: {
	// 				items: 3
	// 			},
	// 			1300: {
	// 				items: 3
	// 			}
	// 		}
	// 	})
	// }

	if ($('.owl-carousel.blog-slider-twelve').length > 0) {
		$('.owl-carousel.blog-slider-twelve').owlCarousel({
			loop: true,
			margin: 24,
			dots: false,
			nav: true,
			smartSpeed: 2000,
			navContainer: '.slide-nav-16',
			rtl: true,
			navText: ['<i class="fa-solid fa-caret-left "></i>', '<i class="fa-solid fa-caret-right"></i>'],
			responsive: {
				0: {
					items: 1
				},
				500: {
					items: 1
				},
				575: {
					items: 2
				},
				768: {
					items: 2
				},
				1000: {
					items: 4
				},
				1300: {
					items: 4
				}
			}
		})
	}

	// Our Doctor
	if ($('.owl-carousel.our-slider-thirteen').length > 0) {
		$('.owl-carousel.our-slider-thirteen').owlCarousel({
			loop: true,
			margin: 64,
			dots: true,
			nav: false,
			smartSpeed: 2000,
			rtl: true,
			responsive: {
				0: {
					items: 1
				},
				500: {
					items: 1
				},
				575: {
					items: 2
				},
				768: {
					items: 2
				},
				1000: {
					items: 3
				},
				1300: {
					items: 3
				}
			}
		})
	}

	// Doctor Slider

	if ($('.owl-carousel.doctor-slider-fifteen').length > 0) {
		$('.owl-carousel.doctor-slider-fifteen').owlCarousel({
			loop: true,
			margin: 24,
			dots: false,
			nav: true,
			smartSpeed: 2000,
			rtl: true,
			navText: ['<i class="fas fa-chevron-right"></i>', '<i class="fas fa-chevron-left"></i>'],
			responsive: {
				0: {
					items: 1
				},
				500: {
					items: 1
				},
				575: {
					items: 1
				},
				768: {
					items: 2
				},
				1000: {
					items: 3
				},
				1300: {
					items: 3
				}
			}
		})
	}

	if ($('.owl-carousel.client-says-thirteen').length > 0) {
		$('.owl-carousel.client-says-thirteen').owlCarousel({
			loop: true,
			margin: 24,
			dots: true,
			nav: false,
			smartSpeed: 2000,
			rtl: true,
			responsive: {
				0: {
					items: 1
				},
				500: {
					items: 1
				},
				575: {
					items: 1
				},
				768: {
					items: 1
				},
				1000: {
					items: 1
				},
				1300: {
					items: 1
				}
			}
		})
	}

	// Doctor Slider

	if ($('.owl-carousel.pharmacy-slider-fifteen').length > 0) {
		$('.owl-carousel.pharmacy-slider-fifteen').owlCarousel({
			loop: true,
			margin: 24,
			dots: false,
			nav: true,
			smartSpeed: 2000,
			rtl: true,
			navText: ['<i class="fas fa-chevron-right"></i>', '<i class="fas fa-chevron-left"></i>'],
			responsive: {
				0: {
					items: 1
				},
				500: {
					items: 1
				},
				575: {
					items: 1
				},
				768: {
					items: 2
				},
				1000: {
					items: 3
				},
				1300: {
					items: 3
				}
			}
		})
	}

	//Eye Testimonial carousel

	if ($('.owl-carousel.eye-testislider').length > 0) {
		$('.owl-carousel.eye-testislider').owlCarousel({
			loop: true,
			margin: 15,
			dots: false,
			nav: true,
			smartSpeed: 2000,
			navContainer: '.slide-11',
			rtl: true,
			navText: ['<i class="fa-solid fa-arrow-right"></i>', '<i class="fa-solid fa-arrow-left"></i>'],
			responsive: {
				0: {
					items: 1
				},
				1300: {
					items: 1
				}
			}
		})
	}

	// Feedback Slider

	if ($('.owl-carousel.feedback-slider-fourteen').length > 0) {
		$('.owl-carousel.feedback-slider-fourteen').owlCarousel({
			loop: true,
			margin: 24,
			dots: false,
			nav: true,
			smartSpeed: 2000,
			rtl: true,
			navText: ['<i class="fa-solid fa-caret-right"></i>', '<i class="fa-solid fa-caret-left "></i>'],
			responsive: {
				0: {
					items: 1
				},
				500: {
					items: 1
				},
				768: {
					items: 1
				},
				1000: {
					items: 1
				},
				1300: {
					items: 1
				}
			}
		})
	}

	// Date Slider

	if ($('.date-slider').length > 0) {
		$('.date-slider').slick({
			dots: false,
			autoplay: false,
			infinite: true,
			rtl: true,
			variableWidth: false,
			slidesToShow: 7,
			slidesToScroll: 1,
			swipeToSlide: true,
			responsive: [
				{
					breakpoint: 1024,
					settings: {
						slidesToShow: 3,
						slidesToScroll: 1
					}
				},
				{
					breakpoint: 992,
					settings: {
						slidesToShow: 3,
						slidesToScroll: 1
					}
				},
				{
					breakpoint: 768,
					settings: {
						slidesToShow: 3,
						slidesToScroll: 1
					}
				},
				{
					breakpoint: 500,
					settings: {
						slidesToShow: 1,
						slidesToScroll: 1
					}
				}
			]
		});
	}

	// Testimonial Slider

	if ($('.testimonial-slider').length > 0) {
		$('.testimonial-slider').slick({
			dots: false,
			autoplay: false,
			infinite: true,
			speed: 2000,
			rtl: true,
			variableWidth: false,
			slidesToShow: 1,
			slidesToScroll: 1,
			swipeToSlide: true,
			responsive: [
				{
					breakpoint: 1024,
					settings: {
						slidesToShow: 1,
						slidesToScroll: 1
					}
				},
				{
					breakpoint: 992,
					settings: {
						slidesToShow: 1,
						slidesToScroll: 1
					}
				},
				{
					breakpoint: 768,
					settings: {
						slidesToShow: 1,
						slidesToScroll: 1
					}
				},
				{
					breakpoint: 500,
					settings: {
						slidesToShow: 1,
						slidesToScroll: 1
					}
				}
			]
		});
	}

	// Partners Slider

	if ($('.owl-carousel.partners-slider').length > 0) {
		$('.owl-carousel.partners-slider').owlCarousel({
			loop: true,
			margin: 24,
			nav: true,
			rtl: true,
			autoplay: true,
			smartSpeed: 2000,
			responsive: {
				0: {
					items: 1
				},

				550: {
					items: 2
				},
				700: {
					items: 4
				},
				1000: {
					items: 6
				}
			}
		})
	}

	// Frequent Slider

	if ($('.owl-carousel.frequent-slider-fifteen').length > 0) {
		$('.owl-carousel.frequent-slider-fifteen').owlCarousel({
			loop: true,
			margin: 24,
			dots: true,
			nav: true,
			smartSpeed: 2000,
			rtl: true,
			navText: ['<i class="fas fa-chevron-right"></i>', '<i class="fas fa-chevron-left"></i>'],
			responsive: {
				0: {
					items: 1
				},
				500: {
					items: 1
				},
				768: {
					items: 2
				},
				1000: {
					items: 3
				},
				1300: {
					items: 3
				}
			}
		})
	}


	// Team Slider
	if ($('.owl-carousel.team-fourteen-slider').length > 0) {
		$('.owl-carousel.team-fourteen-slider').owlCarousel({
			loop: true,
			margin: 24,
			dots: false,
			nav: true,
			smartSpeed: 2000,
			rtl: true,
			navContainer: '.slide-nav-14',
			navText: ['<i class="fa-solid fa-caret-left "></i>', '<i class="fa-solid fa-caret-right"></i>'],
			responsive: {
				0: {
					items: 1
				},
				500: {
					items: 1
				},
				768: {
					items: 2
				},
				1000: {
					items: 2
				},
				1300: {
					items: 2
				}
			}
		})
	}

	// Blog Slider

	if ($('.owl-carousel.blog-slider-fourteen').length > 0) {
		$('.owl-carousel.blog-slider-fourteen').owlCarousel({
			loop: true,
			margin: 24,
			dots: false,
			nav: true,
			smartSpeed: 2000,
			navContainer: '.slide-nav-15',
			rtl: true,
			navText: ['<i class="fa-solid fa-caret-right "></i>', '<i class="fa-solid fa-caret-left"></i>'],
			responsive: {
				0: {
					items: 1
				},
				500: {
					items: 1
				},
				575: {
					items: 2
				},
				768: {
					items: 2
				},
				1000: {
					items: 3
				},
				1300: {
					items: 3
				}
			}
		})
	}

	// Discover Slider

	if ($('.owl-carousel.discover-slider').length > 0) {
		$('.owl-carousel.discover-slider').owlCarousel({
			loop: true,
			margin: 10,
			dots: true,
			nav: false,
			smartSpeed: 2000,
			rtl: true,
			responsive: {
				0: {
					items: 1
				},
				500: {
					items: 1
				},
				575: {
					items: 2
				},
				768: {
					items: 2
				},
				1000: {
					items: 3
				},
				1300: {
					items: 5
				}
			}
		})
	}

	// Treatment Slider

	if ($('.owl-carousel.treatment-sixteen-slider').length > 0) {
		$('.owl-carousel.treatment-sixteen-slider').owlCarousel({
			loop: true,
			margin: 10,
			dots: true,
			nav: false,
			smartSpeed: 2000,
			rtl: true,
			responsive: {
				0: {
					items: 1
				},
				500: {
					items: 1
				},
				575: {
					items: 2
				},
				768: {
					items: 2
				},
				1000: {
					items: 3
				},
				1300: {
					items: 4
				}
			}
		})
	}


	//Choose Slider
	if ($('.about-us-section-fifteen .vertical-slider').length > 0) {
		$('.about-us-section-fifteen .vertical-slider').slick({
			dots: true,
			arrows: true,
			autoplay: false,
			centerMode: true,
			infinite: true,
			rows: 0,
			slidesToShow: 3,
			vertical: true,
			verticalSwiping: true
		});
	}

	//slider
	if ($(' #slide-experts').length > 0) {
		$('#slide-experts').owlCarousel({
			margin: 0,
			center: true,
			loop: true,
			nav: false,
			dots: false,
			rtl: true,
			responsive: {
				0: {
					items: 1
				},
				768: {
					items: 1,
					margin: 15,
				},
				1000: {
					items: 3,
				}
			}
		});
	};

	// Feedback Slider

	if ($('.owl-carousel.feedback-slider-fourteen').length > 0) {
		$('.owl-carousel.feedback-slider-fourteen').owlCarousel({
			loop: true,
			margin: 24,
			dots: false,
			nav: true,
			smartSpeed: 2000,
			rtl: true,
			navText: ['<i class="fa-solid fa-caret-right"></i>', '<i class="fa-solid fa-caret-left "></i>'],
			responsive: {
				0: {
					items: 1
				},
				500: {
					items: 1
				},
				768: {
					items: 1
				},
				1000: {
					items: 1
				},
				1300: {
					items: 1
				}
			}
		})
	}


	// Slick Slider

	// if ($('.specialities-slider').length > 0) {
	// 	$('.specialities-slider').slick({
	// 		dots: true,
	// 		autoplay: false,
	// 		infinite: true,
	// 		slidesToShow: 5,
	// 		slidesToScroll: 1,
	// 		prevArrow: false,
	// 		nextArrow: false,
	// 		rtl: true,
	// 		rows: 1,
	// 		responsive: [{
	// 			breakpoint: 1199,
	// 			settings: {
	// 				slidesToShow: 4
	// 			}
	// 		},
	// 		{
	// 			breakpoint: 991,
	// 			settings: {
	// 				slidesToShow: 3
	// 			}
	// 		},
	// 		{
	// 			breakpoint: 776,
	// 			settings: {
	// 				slidesToShow: 3
	// 			}
	// 		},
	// 		{
	// 			breakpoint: 567,
	// 			settings: {
	// 				slidesToShow: 2
	// 			}
	// 		}
	// 	]
	// 	});
	// }

	if ($('.specialities-slider').length > 0) {
		$('.specialities-slider').slick({
			dots: true,
			autoplay: false,
			infinite: true,
			slidesToShow: 5,
			slidesToScroll: 1,
			prevArrow: false,
			nextArrow: false,
			rtl: true,
			rows: 1,
			responsive: [{
				breakpoint: 1199,
				settings: {
					slidesToShow: 4
				}
			},
			{
				breakpoint: 991,
				settings: {
					slidesToShow: 3
				}
			},
			{
				breakpoint: 776,
				settings: {
					slidesToShow: 3
				}
			},
			{
				breakpoint: 567,
				settings: {
					slidesToShow: 2
				}
			}
		]
		});
	}


	if ($('.doctor-slider').length > 0) {
		$('.doctor-slider').slick({
			dots: false,
			autoplay: false,
			rtl: true,
			infinite: true,
			variableWidth: true,
			slidesToShow: 3,
			speed: 500,
			variableWidth: false,
			autoplay: false,
			responsive: [{
				breakpoint: 992,
				settings: {
					slidesToShow: 3
				}
			},
			{
				breakpoint: 800,
				settings: {
					slidesToShow: 3
				}
			},
			{
				breakpoint: 776,
				settings: {
					slidesToShow: 2
				}
			},
			{
				breakpoint: 567,
				settings: {
					slidesToShow: 1
				}
			}]
		});
	}

	if ($('.features-slider').length > 0) {
		$('.features-slider').slick({
			dots: true,
			infinite: true,
			centerMode: true,
			slidesToShow: 3,
			rtl: true,
			speed: 500,
			variableWidth: true,
			arrows: false,
			autoplay: false,
			responsive: [{
				breakpoint: 992,
				settings: {
					slidesToShow: 1
				}

			}]
		});
	}

	// Load More Timings Open

	$(".time-slot-morning").slideUp();
	$(".load-more-morning").on("click", function () {
		$(this).toggleClass("show");
		$(".time-slot-morning").slideToggle();
	});

	$(".time-slot-afternoon").slideUp();
	$(".load-more-afternoon").on("click", function () {
		$(this).toggleClass("show");
		$(".time-slot-afternoon").slideToggle();
	});

	$(".time-slot-evening").slideUp();
	$(".load-more-evening").on("click", function () {
		$(this).toggleClass("show");
		$(".time-slot-evening").slideToggle();
	});


	// Slick Slider
	if ($('.features-slider1').length == 1) {
		$('.features-slider1').slick({
			dots: false,
			infinite: true,
			centerMode: false,
			slidesToShow: 1,
			rtl: true,
			speed: 500,
			variableWidth: true,
			arrows: true,
			autoplay: false,
			responsive: [{
				breakpoint: 992,
				settings: {
					slidesToShow: 1
				}

			}]
		});
	}
	if ($('.slider-1').length > 0) {
		$('.slider-1').slick(
			{
				rtl: true,
			}
		);
	}

	//Home pharmacy slider
	if ($('.dot-slider').length > 0) {
		$('.dot-slider').slick({
			dots: true,
			autoplay: false,
			infinite: true,
			rtl: true,
			slidesToShow: 1,
			slidesToScroll: 1,
			arrows: false,
			responsive: [{
				breakpoint: 992,
				settings: {
					slidesToShow: 1
				}
			},
			{
				breakpoint: 800,
				settings: {
					slidesToShow: 1
				}
			},
			{
				breakpoint: 776,
				settings: {
					slidesToShow: 1
				}
			},
			{
				breakpoint: 567,
				settings: {
					slidesToShow: 1
				}
			}]
		});
	}

	//clinic slider
	if ($('.clinic-slider').length > 0) {
		$('.clinic-slider').slick({
			dots: false,
			autoplay: false,
			infinite: true,
			slidesToShow: 4,
			rtl: true,
			slidesToScroll: 1,
			rows: 2,
			responsive: [{
				breakpoint: 992,
				settings: {
					slidesToShow: 3
				}
			},
			{
				breakpoint: 800,
				settings: {
					slidesToShow: 3
				}
			},
			{
				breakpoint: 776,
				settings: {
					slidesToShow: 3
				}
			},
			{
				breakpoint: 567,
				settings: {
					slidesToShow: 1
				}
			}]
		});
	}

	//browse slider
	if ($('.browse-slider').length > 0) {
		$('.browse-slider').slick({
			dots: false,
			autoplay: false,
			infinite: true,
			slidesToShow: 4,
			rtl: true,
			slidesToScroll: 1,
			rows: 2,
			responsive: [{
				breakpoint: 992,
				settings: {
					slidesToShow: 3
				}
			},
			{
				breakpoint: 800,
				settings: {
					slidesToShow: 3
				}
			},
			{
				breakpoint: 776,
				settings: {
					slidesToShow: 3
				}
			},
			{
				breakpoint: 567,
				settings: {
					slidesToShow: 1
				}
			}]
		});
	}

	//book doctor slider
	if ($('.book-slider').length > 0) {
		$('.book-slider').slick({
			dots: false,
			autoplay: false,
			infinite: true,
			slidesToShow: 4,
			rtl: true,
			slidesToScroll: 1,
			responsive: [{
				breakpoint: 992,
				settings: {
					slidesToShow: 3
				}
			},
			{
				breakpoint: 800,
				settings: {
					slidesToShow: 3
				}
			},
			{
				breakpoint: 776,
				settings: {
					slidesToShow: 2
				}
			},
			{
				breakpoint: 567,
				settings: {
					slidesToShow: 1
				}
			}]
		});
	}

	//avalable features slider
	if ($('.aval-slider').length > 0) {
		$('.aval-slider').slick({
			dots: false,
			autoplay: false,
			infinite: true,
			slidesToShow: 3,
			rtl: true,
			slidesToScroll: 1,
			responsive: [{
				breakpoint: 992,
				settings: {
					slidesToShow: 2
				}
			},
			{
				breakpoint: 800,
				settings: {
					slidesToShow: 2
				}
			},
			{
				breakpoint: 776,
				settings: {
					slidesToShow: 2
				}
			},
			{
				breakpoint: 567,
				settings: {
					slidesToShow: 1
				}
			}]
		});
	}
	//Home pharmacy slider
	if ($('.pharmacy-home-slider .swiper-container').length > 0) {
		var swiper = new Swiper('.pharmacy-home-slider .swiper-container', {
			loop: true,
			speed: 1000,
			rtl: true,
			pagination: {
				el: '.pharmacy-home-slider .swiper-pagination',
				dynamicBullets: true,
				clickable: true,
			},
			navigation: {
				nextEl: '.pharmacy-home-slider .swiper-button-next',
				prevEl: '.pharmacy-home-slider .swiper-button-prev',
			},
		});
	}

	// Date Range Picker
	if ($('.bookingrange').length > 0) {
		var start = moment().subtract(6, 'days');
		var end = moment();

		function booking_range(start, end) {
			$('.bookingrange span').html(start.format('MMMM D, YYYY') + ' - ' + end.format('MMMM D, YYYY'));
		}

		$('.bookingrange').daterangepicker({
			startDate: start,
			endDate: end,
			ranges: {
				'Today': [moment(), moment()],
				'Yesterday': [moment().subtract(1, 'days'), moment().subtract(1, 'days')],
				'Last 7 Days': [moment().subtract(6, 'days'), moment()],
				'Last 30 Days': [moment().subtract(29, 'days'), moment()],
				'This Month': [moment().startOf('month'), moment().endOf('month')],
				'Last Month': [moment().subtract(1, 'month').startOf('month'), moment().subtract(1, 'month').endOf('month')]
			}
		}, booking_range);

		booking_range(start, end);
	}
	// Chat

	var chatAppTarget = $('.chat-window');
	(function () {
		if ($(window).width() > 991)
			chatAppTarget.removeClass('chat-slide');

		$(document).on("click", ".chat-window .chat-users-list a.media", function () {
			if ($(window).width() <= 991) {
				chatAppTarget.addClass('chat-slide');
			}
			return false;
		});
		$(document).on("click", "#back_user_list", function () {
			if ($(window).width() <= 991) {
				chatAppTarget.removeClass('chat-slide');
			}
			return false;
		});
	})();

//Increment Decrement Numberes
var quantity = 0;
$('.quantity-right-plus').click(function (e) {
	e.preventDefault();
	var quantity = parseInt($('#quantity').val());
	$('#quantity').val(quantity + 1);
});

$('.quantity-left-minus').click(function (e) {
	e.preventDefault();
	var quantity = parseInt($('#quantity').val());
	if (quantity > 0) {
		$('#quantity').val(quantity - 1);
	}
});

var quantity2 = 0;
$('.quantity-right-plus2').click(function (e) {
	e.preventDefault();
	var quantity2 = parseInt($('#quantity2').val());
	$('#quantity2').val(quantity2 + 1);
});

$('.quantity-left-minus2').click(function (e) {
	e.preventDefault();
	var quantity2 = parseInt($('#quantity2').val());
	if (quantity2 > 0) {
		$('#quantity2').val(quantity2 - 1);
	}
});

var quantity3 = 0;
$('.quantity-right-plus3').click(function (e) {
	e.preventDefault();
	var quantity3 = parseInt($('#quantity3').val());
	$('#quantity3').val(quantity3 + 1);
});

$('.quantity-left-minus3').click(function (e) {
	e.preventDefault();
	var quantity3 = parseInt($('#quantity3').val());
	if (quantity3 > 0) {
		$('#quantity3').val(quantity3 - 1);
	}
});

var quantity4 = 0;
$('.quantity-right-plus4').click(function (e) {
	e.preventDefault();
	var quantity4 = parseInt($('#quantity4').val());
	$('#quantity4').val(quantity4 + 1);
});

$('.quantity-left-minus4').click(function (e) {
	e.preventDefault();
	var quantity4 = parseInt($('#quantity4').val());
	if (quantity4 > 0) {
		$('#quantity4').val(quantity4 - 1);
	}
});

var quantity5 = 0;
$('.quantity-right-plus5').click(function (e) {
	e.preventDefault();
	var quantity5 = parseInt($('#quantity5').val());
	$('#quantity5').val(quantity5 + 1);
});

$('.quantity-left-minus5').click(function (e) {
	e.preventDefault();
	var quantity5 = parseInt($('#quantity5').val());
	if (quantity5 > 0) {
		$('#quantity5').val(quantity5 - 1);
	}
});

	//Cart Click
	$("#cart").on("click", function (o) {
		o.preventDefault();
		$(".shopping-cart").fadeToggle();
		$(".shopping-cart").toggleClass('show-cart');
	});

	// Circle Progress Bar

	function animateElements() {
		$('.circle-bar1').each(function () {
			var elementPos = $(this).offset().top;
			var topOfWindow = $(window).scrollTop();
			var percent = $(this).find('.circle-graph1').attr('data-percent');
			var animate = $(this).data('animate');
			if (elementPos < topOfWindow + $(window).height() - 30 && !animate) {
				$(this).data('animate', true);
				$(this).find('.circle-graph1').circleProgress({
					value: percent / 100,
					size: 400,
					thickness: 30,
					fill: {
						color: '#da3f81'
					}
				});
			}
		});
		$('.circle-bar2').each(function () {
			var elementPos = $(this).offset().top;
			var topOfWindow = $(window).scrollTop();
			var percent = $(this).find('.circle-graph2').attr('data-percent');
			var animate = $(this).data('animate');
			if (elementPos < topOfWindow + $(window).height() - 30 && !animate) {
				$(this).data('animate', true);
				$(this).find('.circle-graph2').circleProgress({
					value: percent / 100,
					size: 400,
					thickness: 30,
					fill: {
						color: '#68dda9'
					}
				});
			}
		});
		$('.circle-bar3').each(function () {
			var elementPos = $(this).offset().top;
			var topOfWindow = $(window).scrollTop();
			var percent = $(this).find('.circle-graph3').attr('data-percent');
			var animate = $(this).data('animate');
			if (elementPos < topOfWindow + $(window).height() - 30 && !animate) {
				$(this).data('animate', true);
				$(this).find('.circle-graph3').circleProgress({
					value: percent / 100,
					size: 400,
					thickness: 30,
					fill: {
						color: '#1b5a90'
					}
				});
			}
		});
	}

	if ($('.circle-bar').length > 0) {
		animateElements();
	}
	$(window).scroll(animateElements);

	// Preloader

	$(window).on('load', function () {
		if ($('#loader').length > 0) {
			$('#loader').delay(350).fadeOut('slow');
			$('body').delay(350).css({ 'overflow': 'visible' });
		}
	})

	//owl carousel

	if ($('.owl-carousel.clinics').length > 0) {
		$('.owl-carousel.clinics').owlCarousel({
			loop: true,
			margin: 15,
			dots: false,
			nav: true,
			rtl: true,
			navContainer: '.slide-nav-1',
			navText: ['<i class="fas fa-chevron-left custom-arrow"></i>', '<i class="fas fa-chevron-right custom-arrow"></i>'],
			responsive: {
				0: {
					items: 1
				},
				500: {
					items: 1
				},
				768: {
					items: 3
				},
				1000: {
					items: 4
				},
				1300: {
					items: 6
				}
			}
		})
	}
	if ($('.owl-carousel.our-doctors').length > 0) {
		$('.owl-carousel.our-doctors').owlCarousel({
			loop: true,
			margin: 15,
			dots: false,
			nav: true,
			rtl: true,
			navContainer: '.slide-nav-2',
			navText: ['<i class="fas fa-chevron-left custom-arrow"></i>', '<i class="fas fa-chevron-right custom-arrow"></i>'],
			responsive: {
				0: {
					items: 1
				},
				500: {
					items: 1
				},
				768: {
					items: 2
				},
				1000: {
					items: 3
				},
				1300: {
					items: 4
				}
			}
		})
	}
	if ($('.owl-carousel.clinic-feature').length > 0) {
		$('.owl-carousel.clinic-feature').owlCarousel({
			loop: true,
			margin: 15,
			dots: false,
			nav: true,
			rtl: true,
			navContainer: '.slide-nav-3',
			navText: ['<i class="fas fa-chevron-left custom-arrow"></i>', '<i class="fas fa-chevron-right custom-arrow"></i>'],
			responsive: {
				0: {
					items: 1
				},
				500: {
					items: 1
				},
				768: {
					items: 3
				},
				1000: {
					items: 4
				},
				1300: {
					items: 5
				}
			}
		})
	}
	if ($('.owl-carousel.blogs').length > 0) {
		$('.owl-carousel.blogs').owlCarousel({
			loop: true,
			margin: 15,
			dots: false,
			nav: true,
			rtl: true,
			navContainer: '.slide-nav-4',
			navText: ['<i class="fas fa-chevron-left custom-arrow"></i>', '<i class="fas fa-chevron-right custom-arrow"></i>'],
			responsive: {
				0: {
					items: 1
				},
				500: {
					items: 1
				},
				768: {
					items: 2
				},
				1000: {
					items: 3
				},
				1300: {
					items: 4
				}
			}
		})
	}

	//header-fixed

	if ($('.header-trans.header-eight').length > 0) {
		$(document).ready(function () {
			$(window).scroll(function () {
				var scroll = $(window).scrollTop();
				if (scroll > 95) {
					$(".header-trans").css("background", "#ffffff");
				}

				else {
					$(".header-trans").css("background", "transparent");
				}
			})
		})
	}

	if ($('.header-trans.header-two').length > 0) {
		$(document).ready(function () {
			$(window).scroll(function () {
				var scroll = $(window).scrollTop();
				if (scroll > 95) {
					$(".header-trans").css("background", "#ffffff");
				}

				else {
					$(".header-trans").css("background", "transparent");
				}
			})
		})
	}

	//header-fixed

	if ($('.header-trans').length > 0) {
		$(document).ready(function () {
			$(window).scroll(function () {
				var scroll = $(window).scrollTop();
				if (scroll > 95) {
					$(".header-trans").css("background", "#FFFFFF");
				}

				else {
					$(".header-trans").css("background", "transparent");
				}
			})
		})
	}

	if ($('.header-ten').length > 0) {
		$(document).ready(function () {
			$(window).scroll(function () {
				var scroll = $(window).scrollTop();
				if (scroll > 35) {
					$(".header-ten").addClass('header-space');
				}

				else {
					$(".header-ten").removeClass('header-space');
				}
			})
		})
	}
	if ($('.header-trans.custom').length > 0) {
		$(document).ready(function () {
			$(window).scroll(function () {
				var scroll = $(window).scrollTop();
				if (scroll > 95) {
					$(".header-trans").css("background", "#2b6ccb");
				}

				else {
					$(".header-trans").css("background", "transparent");
				}
			})
		})
	}

	// Header Fixed

	if ($('.header-fourteen').length > 0) {
		$(document).ready(function () {
			$(window).scroll(function () {
				var scroll = $(window).scrollTop();
				if (scroll > 95) {
					$(".header-fourteen").css("background", "#2b6ccb");
				}

				else {
					$(".header-fourteen").css("background", "transparent");
				}
			})
		})
	}

	// Header Fixed

	if ($('.header-fourteen.header-fifteen').length > 0) {
		$(document).ready(function () {
			$(window).scroll(function () {
				var scroll = $(window).scrollTop();
				if (scroll > 95) {
					$(".header-fourteen.header-fifteen").css("background", "#FFFFFF");
				}

				else {
					$(".header-fourteen.header-fifteen").css("background", "transparent");
				}
			})
		})
	}
	
	if ($('.header-fourteen.header-twelve').length > 0) {
		$(document).ready(function () {
			$(window).scroll(function () {
				var scroll = $(window).scrollTop();
				if (scroll > 95) {
					$(".header-fourteen").css("background", "#fff");
				}

				else {
					$(".header-fourteen").css("background", "transparent");
				}
			})
		})
	}

	// Header Fixed

	if ($('.header-one').length > 0) {
		$(document).ready(function () {
			$(window).scroll(function () {
				var scroll = $(window).scrollTop();
				if (scroll > 35) {
					$(".header-one").addClass('header-space');
				}

				else {
					$(".header-one").removeClass('header-space');
				}
			})
		})
	}

	if ($('.header-trans.header-eleven').length > 0) {
		$(document).ready(function () {
			$(window).scroll(function () {
				var scroll = $(window).scrollTop();
				if (scroll > 95) {
					$(".header-trans").css("background", "#1e5d92");
				}

				else {
					$(".header-trans").css("background", "transparent");
				}
			})
		})
	}
	if ($('.header-sixteen').length > 0) {
		$(document).ready(function () {
			$(window).scroll(function () {
				var scroll = $(window).scrollTop();
				if (scroll > 95) {
					$(".header-sixteen").css("background", "#ffffff");
				}

				else {
					$(".header-sixteen").css("background", "transparent");
				}
			})
		})
	}
	if ($('.header-fourteen.header-twelve').length > 0) {
		$(document).ready(function () {
			$(window).scroll(function () {
				var scroll = $(window).scrollTop();
				if (scroll > 95) {
					$(".header-fourteen").css("background", "#fff");
				}

				else {
					$(".header-fourteen").css("background", "transparent");
				}
			})
		})
	}
	if ($('.header-fourteen.header-thirteen').length > 0) {
		$(document).ready(function () {
			$(window).scroll(function () {
				var scroll = $(window).scrollTop();
				if (scroll > 95) {
					$(".header-fourteen").css("background", "#fff");
				}

				else {
					$(".header-fourteen").css("background", "#fff");
				}
			})
		})
	}

	//for slider
	$(window).on('load resize', function () {
		var window_width = $(window).outerWidth();
		var container_width = $('.container').outerWidth();
		var full_width = window_width - container_width
		var right_position_value = full_width / 2
		$('.slider-service').css('padding-left', right_position_value);

	});

	//BMI Status
	if ($('#bmi-status').length > 0) {
		var options = {
			series: [{
				name: "BMI",
				data: [10, 41, 35, 51, 49, 62, 69, 91, 148]
			}],
			chart: {
				height: 350,
				type: 'line',
				zoom: {
					enabled: false
				}
			},
			dataLabels: {
				enabled: false
			},
			stroke: {
				curve: 'straight'
			},
			title: {
				align: 'left'
			},
			grid: {
				row: {
					colors: ['#f3f3f3', 'transparent'], // takes an array which will be repeated on columns
					opacity: 0.5
				},
			},
			xaxis: {
				categories: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep'],
			}
		};

		var chart = new ApexCharts(document.querySelector("#bmi-status"), options);
		chart.render();
	}

	//Heart Rate Status
	if ($('#heartrate-status').length > 0) {
		var options = {
			series: [{
				name: 'HeartRate',
				data: [4, 3, 10, 9, 29, 19, 22, 9, 12, 7, 19, 5, 13, 9, 17, 2, 7, 5]
			}],
			chart: {
				height: 350,
				type: 'line',
			},
			stroke: {
				width: 7,
				curve: 'smooth'
			},
			xaxis: {
				type: 'datetime',
				categories: ['1/11/2000', '2/11/2000', '3/11/2000', '4/11/2000', '5/11/2000', '6/11/2000', '7/11/2000', '8/11/2000', '9/11/2000', '10/11/2000', '11/11/2000', '12/11/2000', '1/11/2001', '2/11/2001', '3/11/2001', '4/11/2001', '5/11/2001', '6/11/2001'],
				tickAmount: 10,
			},
			title: {
				align: 'left',
			},
			fill: {
				type: 'gradient',
				gradient: {
					shade: 'dark',
					gradientToColors: ['#0de0fe'],
					shadeIntensity: 1,
					type: 'horizontal',
					opacityFrom: 1,
					opacityTo: 1,
					stops: [0, 100, 100, 100]
				},
			},
			markers: {
				size: 4,
				colors: ["#15558d"],
				strokeColors: "#fff",
				strokeWidth: 2,
				hover: {
					size: 7,
				}
			},
			yaxis: {
				min: -10,
				max: 40,
				title: {
				},
			}
		};

		var chart = new ApexCharts(document.querySelector("#heartrate-status"), options);
		chart.render();
	}

	//FBC Status
	if ($('#fbc-status').length > 0) {
		var options = {
			series: [{
				name: 'FBC',
				data: [2.3, 3.1, 4.0, 10.1, 4.0, 3.6, 3.2, 2.3, 1.4, 0.8, 0.5, 0.2]
			}],
			chart: {
				height: 350,
				type: 'bar',
			},
			plotOptions: {
				bar: {
					borderRadius: 10,
					dataLabels: {
						position: 'top', // top, center, bottom
					},
				}
			},
			dataLabels: {
				enabled: true,
				formatter: function (val) {
					return val + "%";
				},
				offsetY: -20,
				style: {
					fontSize: '12px',
					colors: ["#304758"]
				}
			},

			xaxis: {
				categories: ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
				position: 'top',
				axisBorder: {
					show: false
				},
				axisTicks: {
					show: false
				},
				crosshairs: {
					fill: {
						type: 'gradient',
						gradient: {
							colorFrom: '#0de0fe',
							colorTo: '#0de0fe',
							stops: [0, 100],
							opacityFrom: 0.4,
							opacityTo: 0.5,
						}
					}
				},
				tooltip: {
					enabled: true,
				}
			},
			yaxis: {
				axisBorder: {
					show: false
				},
				axisTicks: {
					show: false,
				},
				labels: {
					show: false,
					formatter: function (val) {
						return val + "%";
					}
				}

			},
			title: {
				floating: true,
				offsetY: 330,
				align: 'center',
				style: {
					color: '#444'
				}
			}
		};

		var chart = new ApexCharts(document.querySelector("#fbc-status"), options);
		chart.render();
	}

	//Weight Status
	if ($('#weight-status').length > 0) {
		var options = {
			series: [{
				name: 'Weight',
				data: [34, 44, 54, 21, 12, 43, 33, 23, 66, 66, 58]
			}],
			chart: {
				type: 'line',
				height: 350
			},
			stroke: {
				curve: 'stepline',
			},
			dataLabels: {
				enabled: false
			},
			title: {
				align: 'left'
			},
			markers: {
				hover: {
					sizeOffset: 4
				}
			}
		};

		var chart = new ApexCharts(document.querySelector("#weight-status"), options);
		chart.render();
	}

	// Signup Toggle
	$(function () {
		$("#is_registered").click(function () {
			if ($(this).is(":checked")) {
				$("#preg_div").show();
			} else {
				$("#preg_div").hide();
			}
		});
	});

	//Increment Decrement value
	$('.inc.button').click(function () {
		var $this = $(this),
			$input = $this.prev('input'),
			$parent = $input.closest('div'),
			newValue = parseInt($input.val()) + 1;
		$parent.find('.inc').addClass('a' + newValue);
		$input.val(newValue);
		newValue += newValue;
	});
	$('.dec.button').click(function () {
		var $this = $(this),
			$input = $this.next('input'),
			$parent = $input.closest('div'),
			newValue = parseInt($input.val()) - 1;
		console.log($parent);
		$parent.find('.inc').addClass('a' + newValue);
		$input.val(newValue);
		newValue += newValue;
	});

	// Signup Profile
	function readURL(input) {
		if (input.files && input.files[0]) {
			var reader = new FileReader();

			reader.onload = function (e) {
				$('#prof-avatar').attr('src', e.target.result);
			};

			reader.readAsDataURL(input.files[0]);
		}
	}
	$("#profile_image").change(function () {
		readURL(this);
	});

	// Datepicker
	var maxDate = $('#maxDate').val();
	if ($('#dob').length > 0) {
		$('#dob').datepicker({
			startView: 2,
			format: 'dd/mm/yyyy',
			autoclose: true,
			todayHighlight: true,
			endDate: maxDate
		});
	}
	if ($('#editdob').length > 0) {
		$('#editdob').datepicker({
			startView: 2,
			format: 'dd/mm/yyyy',
			autoclose: true,
			todayHighlight: true,
			endDate: maxDate
		});
	}

	// Search Bar

	$(document).ready(function () {
		$(".searchbar a").click(function () {
			$(".togglesearch").slideToggle();
			$(".top-search").focus();
		});
	});

	if ($('#more-view2').length > 0) {
		const button = document.getElementById('more-view2');
		const container = document.getElementById('fill-more2');

		let isLess = true;

		function showMoreLess() {
			if (isLess) {
				isLess = false;
				container.style.height = 'auto';
				button.innerHTML = "Show less <i class='feather-chevrons-right ms-1'>";
			} else {
				isLess = true;
				container.style.height = '100px';
				button.innerHTML = "Show more <i class='feather-chevrons-right ms-1'></i>";
			}
		}
		button.addEventListener('click', showMoreLess);
	}

	if ($('#more-view').length > 0) {
		const button = document.getElementById('more-view');
		const container = document.getElementById('fill-more');

		let isLess = true;

		function showMoreLess() {
			if (isLess) {
				isLess = false;
				container.style.height = 'auto';
				button.innerHTML = "Show less <i class='feather-chevrons-right ms-1'>";
			} else {
				isLess = true;
				container.style.height = '100px';
				button.innerHTML = "Show more <i class='feather-chevrons-right ms-1'></i>";
			}
		}
		button.addEventListener('click', showMoreLess);
	}

	if ($('#more-view1').length > 0) {
		const button = document.getElementById('more-view1');
		const container = document.getElementById('fill-more1');

		let isLess = true;

		function showMoreLess() {
			if (isLess) {
				isLess = false;
				container.style.height = 'auto';
				button.innerHTML = "Show less <i class='feather-chevrons-right ms-1'>";
			} else {
				isLess = true;
				container.style.height = '100px';
				button.innerHTML = "Show more <i class='feather-chevrons-right ms-1'></i>";
			}
		}
		button.addEventListener('click', showMoreLess);
	}

	$('.favourite-btn .favourite-icon').on('click', function () {
		$(this).toggleClass('favourite');
	});

	$('.favourite-btn-two .favourite-icon-two').on('click', function () {
		$(this).toggleClass('favourite-two');
	});

	// Price Slider

	if ($('#price-range').length > 0) {
		$('#pricerangemin').text(10);
		$('#pricerangemax').text(10000);
		$("#price-range").slider({
			range: true,
			min: 10,
			max: 10000,
			values: [10, 5000],

			slide: function (event, ui) {
				$("#pricerangemin").text(ui.values[0]);
				$("#pricerangemax").text(ui.values[1]);
			}
		});
	}

	// Map

	$("#map-list").on('click', function () {
		$(this).closest(".container").addClass('container-fluid');
		$(this).closest(".container-fluid").removeClass('container');
		$(".map-view").removeClass('col-xl-12').addClass('col-xl-9');
		$(".map-right").css('display', 'block');
		$('.time-slot-slider')[0].slick.refresh();
	});

	// Cursor

	function mim_tm_cursor() {
		var myCursor = jQuery('.mouse-cursor');
		if (myCursor.length) {
			if ($("body")) {
				const e = document.querySelector(".cursor-inner"),
					t = document.querySelector(".cursor-outer");
				let n, i = 0,
					o = !1;
				window.onmousemove = function (s) {
					o || (t.style.transform = "translate(" + s.clientX + "px, " + s.clientY + "px)"), e.style.transform = "translate(" + s.clientX + "px, " + s.clientY + "px)", n = s.clientY, i = s.clientX
				}, $("body").on("mouseenter", "a, .cursor-pointer", function () {
					e.classList.add("cursor-hover"), t.classList.add("cursor-hover")
				}), $("body").on("mouseleave", "a, .cursor-pointer", function () {
					$(this).is("a") && $(this).closest(".cursor-pointer").length || (e.classList.remove("cursor-hover"), t.classList.remove("cursor-hover"))
				}), e.style.visibility = "visible", t.style.visibility = "visible"
			}
		}
	};
	mim_tm_cursor()

	// Slick Slider
	if ($('.onboard-slider').length > 0) {
		$('#onboard-slider').owlCarousel({
			items: 1,
			margin: 30,
			dots: true,
			nav: true,
			navText: false,
			loop: true,
			smartSpeed: 450,
			autoplay: true,
			autoplayTimeout: 5000,
			autoplayHoverPause: true,
			responsiveClass: true,
			responsive: {
				0: {
					items: 1
				},
				768: {
					items: 1
				},
				1170: {
					items: 1
				}
			}
		});
	}

	// Toggle Password

	if ($('.toggle-password').length > 0) {
		$(document).on('click', '.toggle-password', function () {
			$(this).toggleClass("feather-eye");
			var input = $(".pass-input");
			if (input.attr("type") == "password") {
				input.attr("type", "text");
			} else {
				input.attr("type", "password");
			}
		});
	}

	if ($('.toggle-password-sub').length > 0) {
		$(document).on('click', '.toggle-password-sub', function () {
			$(this).toggleClass("feather-eye");
			var input = $(".pass-input-sub");
			if (input.attr("type") == "password") {
				input.attr("type", "text");
			} else {
				input.attr("type", "password");
			}
		});
	}

	// Custom Country Code Selector

	if ($('#phone').length > 0) {
		var input = document.querySelector("#phone");
		window.intlTelInput(input, {
			utilsScript: "assets/plugins/intltelinput/js/utils.js",
		});
	}

	// Custom Country Code Selector

	if ($('#phone-number').length > 0) {
		var input = document.querySelector("#phone-number");
		window.intlTelInput(input, {
			utilsScript: "assets/plugins/intltelinput/js/utils.js",
		});
	}

	// Otp Verfication

	$('.digit-group').find('input').each(function () {
		$(this).attr('maxlength', 1);
		$(this).on('keyup', function (e) {
			var parent = $($(this).parent());

			if (e.keyCode === 8 || e.keyCode === 37) {
				var prev = parent.find('input#' + $(this).data('previous'));

				if (prev.length) {
					$(prev).select();
				}
			} else if ((e.keyCode >= 48 && e.keyCode <= 57) || (e.keyCode >= 65 && e.keyCode <= 90) || (e.keyCode >= 96 && e.keyCode <= 105) || e.keyCode === 39) {
				var next = parent.find('input#' + $(this).data('next'));

				if (next.length) {
					$(next).select();
				} else {
					if (parent.data('autosubmit')) {
						parent.submit();
					}
				}
			}
		});
	});

	$('.digit-group input').on('keyup', function () {
		var self = $(this);
		if (self.val() != '') {
			self.addClass('active');
		} else {
			self.removeClass('active');
		}
	});

	// Doctor Signup Wizard

	let progressVal = 0;
	let businessType = 0;

	$(".next_btn").click(function () {
		$(this).parent().parent().next().fadeIn('slow');
		$(this).parent().parent().css({
			'display': 'none'
		});
		progressVal = progressVal + 1;
		$('.progress-active').removeClass('progress-active').addClass('progress-activated').next().addClass('progress-active');
	});

	$(".prev_btn").click(function () {
		$(this).parent().parent().prev().fadeIn('slow');
		$(this).parent().parent().css({
			'display': 'none'
		});
		progressVal = progressVal - 1;
		$('.progress-active').removeClass('progress-active').prev().removeClass('progress-activated').addClass('progress-active');
	
	});


	// Add More Items

	$(".add-table-items").on('click', '.trash', function () {
		$(this).closest('.test').remove();
		return false;
	});

	$(".add-items").on('click', function () {
			var itemscontent =
			  '<tr class="test">' +
			  "<td>" +
			  '<input type="text" class="form-control">' +
			  "</td>" +
			  "<td>" +
			  '<input type="text" class="form-control">' +
			  "</td>" +
			  "<td>" +
			  '<a href="javascript:void(0)" class="btn bg-danger-light trash remove-btn"><i class="far fa-trash-alt"></i></a>' +
			  "</td>" +
			  "</tr>";
			$(".add-table-items").append(itemscontent);
			return false;
	});

	$(".add-table-prescription").on('click', '.trash', function () {
		$(this).closest('.test').remove();
		return false;
	});
	$(".add-prescription").on('click', function () {
		var itemscontent =
		'<tr class="test">' +
		'<td>' +
			'<input class="form-control" type="text">' +
		'</td>' +
		'<td>' +
			'<input class="form-control" type="text">' +
		'</td>' +
		'<td>' +
			'<input class="form-control" type="text">' +
		'</td>' +
		'<td>' +
			'<div class="form-check form-check-inline">' +
				'<label class="form-check-label">' +
					'<input class="form-check-input" type="checkbox"> Morning' +
				'</label>' +
			'</div>' +
			'<div class="form-check form-check-inline">' +
				'<label class="form-check-label">' +
					'<input class="form-check-input" type="checkbox"> Afternoon' +
				'</label>' +
			'</div>' +
			'<div class="form-check form-check-inline">' +
				'<label class="form-check-label">' +
					'<input class="form-check-input" type="checkbox"> Evening' +
				'</label>' +
			'</div>' +
			'<div class="form-check form-check-inline">' +
				'<label class="form-check-label">' +
					'<input class="form-check-input" type="checkbox"> Night' +
				'</label>' +
			'</div>' +
		'</td>' +
		'<td>' +
			'<a href="#" class="btn bg-danger-light trash"><i class="far fa-trash-alt"></i></a>' +
		'</td>' +
	'</tr>';
		$(".add-table-prescription").append(itemscontent);
		return false;
});

// Mute Audio
	
if($('.mute-bt').length > 0) {
	$(".mute-bt").on('click', function(){
		if($(this).hasClass("stop")) {
			$(this).removeClass("stop");
			$(".mute-bt i").removeClass("feather-mic-off");
			$(".mute-bt i").addClass("feather-mic");
		}
		else{
			$(this).addClass("stop");
			$(".mute-bt i").removeClass("feather-mic");
			$(".mute-bt i").addClass("feather-mic-off");
		}
	});
}

// Mute Video

if($('.mute-video').length > 0) {
	$(".mute-video").on('click', function(){
		if($(this).hasClass("stop")) {
			$(this).removeClass("stop");
			$(".mute-video i").removeClass("feather-video-off");
			$(".mute-video i").addClass("feather-video");
		}
		else{
			$(this).addClass("stop");
			$(".mute-video i").removeClass("feather-video");
			$(".mute-video i").addClass("feather-video-off");
		}
	});
}

if($('.win-maximize').length > 0) {
	$('.win-maximize').on('click', function(e){
		if (!document.fullscreenElement) {
			document.documentElement.requestFullscreen();
		} else {
			if (document.exitFullscreen) {
				document.exitFullscreen();
			}
		}
	})
}
$(document).on("click",".btn-icon",function () {
	$(this).parent().hide();
});
$(document).on("click",".delete_schedule",function () {
	$(this).parent().hide();
});

// Swiper Slider
	
if($('.swiper-slider-banner').length > 0 ){
	var swiper = new Swiper(".swiper-slider-banner", {
		effect: "cards",
		grabCursor: true,
		rtl: true,
		initialSlide: 2,
		loop: false,
		rotate: true,
		mousewheel: {
		invert: false,
	  },
	});
}

// Popular Test Slider

if ($('.popular-test-slider').length > 0) {
	$('.popular-test-slider').owlCarousel({
		loop: false,
		margin: 15,
		rtl: true,
		dots: true,
		nav: false,
		smartSpeed: 2000,
		responsive: {
			0: {
				items: 1
			},
			500: {
				items: 1
			},
			768: {
				items: 2
			},
			1000: {
				items: 3
			},
			1300: {
				items: 4
			}
		}
	})
}

// Doctor Consulting Slider

if ($('.doctor-consulting-slider').length > 0) {
	$('.doctor-consulting-slider').owlCarousel({
		loop: false,
		margin: 15,
		rtl: true,
		dots: false,
		nav: true,
		smartSpeed: 2000,
		navText: ['<i class="fa-solid fa-play"></i>', '<i class="fa-solid fa-play"></i>'],
		responsive: {
			0: {
				items: 1
			},
			500: {
				items: 1
			},
			1300: {
				items: 1
			}
		}
	})
}

// Feature Package Slider

if ($('.feature-package-slider').length > 0) {
	$('.feature-package-slider').owlCarousel({
		loop: false,
		margin: 15,
		dots: false,
		rtl: true,
		nav: true,
		smartSpeed: 2000,
		navText: ['<i class="fa-solid fa-play"></i>', '<i class="fa-solid fa-play"></i>'],
		responsive: {
			0: {
				items: 1
			},
			500: {
				items: 1
			},
			768: {
				items: 2
			},
			1000: {
				items: 3
			},
			1300: {
				items: 3
			}
		}
	})
}

if ($('.best-package-slider').length > 0) {
	$('.best-package-slider').owlCarousel({
		loop: false,
		margin: 15,
		dots: true,
		rtl: true,
		nav: false,
		smartSpeed: 2000,
		responsive: {
			0: {
				items: 1
			},
			500: {
				items: 1
			},
			768: {
				items: 2
			},
			1000: {
				items: 2
			},
			1200: {
				items: 3
			}
		}
	})
}

if ($('.booking-lab-test-slider').length > 0) {
	$('.booking-lab-test-slider').owlCarousel({
		loop: false,
		margin: 15,
		dots: false,
		rtl: true,
		nav: true,
		smartSpeed: 2000,
		navText: ['<i class="fa-solid fa-play"></i>', '<i class="fa-solid fa-play"></i>'],
		responsive: {
			0: {
				items: 1
			},
			500: {
				items: 1
			},
			768: {
				items: 2
			},
			1000: {
				items: 2
			},
			1200: {
				items: 3
			}
		}
	})
}

if ($('.popular-choice-slider').length > 0) {
	$('.popular-choice-slider').owlCarousel({
		loop: false,
		margin: 15,
		dots: false,
		rtl: true,
		nav: true,
		smartSpeed: 2000,
		navText: ['<i class="fa-solid fa-play"></i>', '<i class="fa-solid fa-play"></i>'],
		responsive: {
			0: {
				items: 1
			},
			500: {
				items: 1
			},
			768: {
				items: 2
			},
			1000: {
				items: 3
			},
			1200: {
				items: 4
			}
		}
	})
}

if ($('.nurse-profile-slider').length > 0) {
	$('.nurse-profile-slider').owlCarousel({
		loop: true,
		margin: 24,
		dots: false,
		rtl: true,
		nav: true,
		smartSpeed: 2000,
		navContainer: '.nurse-slide-nav',
		navText: ['<i class="fa-solid fa-chevron-left"></i>', '<i class="fa-solid fa-chevron-right"></i>'],
		responsive: {
			0: {
				items: 1
			},
			500: {
				items: 1
			},
			768: {
				items: 2
			},
			1000: {
				items: 3
			},
			1200: {
				items: 3
			}
		}
	})
}

if ($('.top-nurse-profile-slider').length > 0) {
	$('.top-nurse-profile-slider').owlCarousel({
		loop: true,
		margin: 24,
		dots: false,
		rtl: true,
		nav: true,
		smartSpeed: 2000,
		navContainer: '.top-nurse-slide-nav',
		navText: ['<i class="fa-solid fa-chevron-left"></i>', '<i class="fa-solid fa-chevron-right"></i>'],
		responsive: {
			0: {
				items: 1
			},
			500: {
				items: 1
			},
			768: {
				items: 2
			},
			1000: {
				items: 3
			},
			1200: {
				items: 3
			}
		}
	})
}

if ($('.blog-slide-fourteen').length > 0) {
	$('.blog-slide-fourteen').owlCarousel({
		loop: true,
		margin: 24,
		dots: false,
		rtl: true,
		nav: true,
		smartSpeed: 2000,
		navText: ['<i class="fa-solid fa-chevron-left"></i>', '<i class="fa-solid fa-chevron-right"></i>'],
		responsive: {
			0: {
				items: 1
			},
			500: {
				items: 1
			},
			768: {
				items: 2
			},
			1000: {
				items: 3
			},
			1200: {
				items: 3
			}
		}
	})
}

if ($('.various-logo-slider').length > 0) {
	$('.various-logo-slider').owlCarousel({
		loop: true,
		margin: 24,
		dots: false,
		rtl: true,
		nav: false,
		smartSpeed: 2000,
		responsive: {
			0: {
				items: 1
			},
			500: {
				items: 2
			},
			768: {
				items: 3
			},
			1000: {
				items: 5
			},
			1200: {
				items: 6
			}
		}
	})
}

// Slick Testimonial Two

if ($('.work-video-img').length > 0) {
	$('.work-video-img').slick({
		slidesToShow: 1,
		slidesToScroll: 1,
		arrows: true,
		rtl: true,
		fade: true,
		asNavFor: '.slider-thumbnails-img'
	});
}

if ($('.slider-thumbnails-img').length > 0) {
	$('.slider-thumbnails-img').slick({
		slidesToShow: 3,
		slidesToScroll: 1,
		rtl: true,
		asNavFor: '.work-video-img',
		dots: false,
		arrows: false,
		centerMode: false,
		focusOnSelect: true

	});
}	

// Video Player

$('.treatment-video a').on('click', function () {
	var currentVideo = $(this).parent().find(".doctor-treatment-video").get(0);
	var allVideos = $(".doctor-treatment-video");
	$(this).parent().find(".doctor-treatment-video").toggleClass('active');
	$(this).toggleClass('active');
	allVideos.each(function(){
	   if (currentVideo != this)
	   this.pause();
	});
	if (currentVideo.paused){        
		currentVideo.play();
	} else {       
		currentVideo.pause();
	}
});

})(jQuery);